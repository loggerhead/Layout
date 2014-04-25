import os
import json
import sublime, sublime_plugin

PLUGIN_NAME = 'Layout'
PACKAGES_PATH = sublime.packages_path()
PLUGIN_PATH = os.path.join(PACKAGES_PATH, PLUGIN_NAME)
LAYOUT_PATH = os.path.join(PLUGIN_PATH, 'layouts')

X_MIN, Y_MIN, X_MAX, Y_MAX = (0, 1, 2, 3)


# TODO: remove
def q(*args):
	if args:
		args = [str(arg) for arg in args]
		s = '\t'.join(args)
		s = str(datetime.now()) + '\n\t' + s
	else:
		s = '-' * 80
	with open(os.path.join(PLUGIN_PATH, '_debug.log'), 'a+') as fp:
		fp.write(s + '\n')

# TODO LIST
"""
Enhancement
	resize pane
	save as layout file
	load from layout file
	undo should track `views`
	add move to last_view
	remove ruler when destroy
	add move and layout history
	auto close when move last_view
	auto focus to new pane
	close file when pane destroyed
"""

def Settings():
    return sublime.load_settings('%s.sublime-settings' % PLUGIN_NAME)


class PaneCommand(sublime_plugin.WindowCommand):
	HISTORY = []

	@property
	def layout(self):
		return self.window.get_layout()

	@property
	def cells(self):
		return self.window.get_layout()['cells']

	@property
	def current_group(self):
		return self.window.active_group()

	def get_adjacent_cells(self, group):
		cells = self.cells
		adjacent_cells = {
			'left': [],
			'right': [],
			'up': [],
			'down': [],
		}
		c = cells.pop(group)
		x1, y1, x2, y2 = c[X_MIN], c[Y_MIN], c[X_MAX], c[Y_MAX]

		for ac in cells:
			direction = None
			ax1, ay1, ax2, ay2 = ac[X_MIN], ac[Y_MIN], ac[X_MAX], ac[Y_MAX]
			if (ax1 <= x1 < ax2) or (ax1 < x2 <= ax2):
				if y1 == ay2:
					direction = 'up'
				elif y2 == ay1:
					direction = 'down'
			if (ay1 <= y1 < ay2) or (ay1 < y2 <= ay2):
				if x1 == ax2:
					direction = 'left'
				elif x2 == ax1:
					direction = 'right'
			if direction:
				adjacent_cells[direction].append(ac)

		return adjacent_cells

	def get_open_files(self):
		open_files = []
		for i in range(len(self.cells)):
			views = self.window.views_in_group(i)
			open_files.append([])
			for view in views:
				file_path = view.file_name()
				open_files[i].append(file_path)
		return open_files

	def layout_to_json(self):
		layout = self.layout
		layout['views'] = []
		for i in range(len(layout['cells'])):
			views = self.window.views_in_group(i)
			layout['views'].append(views)
		return json.dumps(layout, indent=2)

	def json_to_layout(self, data):
		return json.loads(data)

	def save_layout_to_file(self, filename):
		# TODO
		pass

	def load_layout_from_file(self, filename):
		# TODO
		pass

	def undo_layout(self):
		last_layout = self.HISTORY.pop()
		self.fixed_set_layout(last_layout)

	def add_history(self):
		max_items = Settings().get('max_history_layout')
		self.HISTORY.append(self.layout)
		if len(self.HISTORY) > max_items:
			self.HISTORY.pop(0)

	def fixed_set_layout(self, layout):
		# A bug was introduced in Sublime Text 3, sometime before 3053,
		# in that it changes the active group to 0 when the layout is changed.
		group = min(self.current_group, self.window.num_groups() - 1)
		self.window.set_layout(layout)
		self.window.focus_group(group)

	def fixed_focus_group(self, group):
		# I have no idea why this is work instead of
		# `self.window.focus_group(group)`
		sublime.set_timeout(lambda : self.window.focus_group(group), 0)
		sublime.set_timeout(lambda : self.window.focus_group(group), 0)

	def split_pane(self, group, pattern, scale):
		rows = self.layout['rows']
		cols = self.layout['cols']
		coord_cells = self.layout['cells']
		value_cells = []

		# (x1, y1) is top left point, (x2, y2) is bottom right point
		try:
			x1, y1, x2, y2 = coord_cells.pop(group)
		except:
			return
		c1, r1, c2, r2 = cols[x1], rows[y1], cols[x2], rows[y2]
		for x1, y1, x2, y2 in coord_cells:
			value_cells.append([cols[x1], rows[y1], cols[x2], rows[y2]])

		new_col = 0
		new_row = 0
		# vertical
		if pattern == 'v':
			new_col = (c2 - c1) * scale + c1
			old_cell = [c1, r1, new_col, r2]
			new_cell = [new_col, r1, c2, r2]
		# horizontal
		elif pattern == 'h':
			new_row = (r2 - r1) * scale + r1
			old_cell = [c1, r1, c2, new_row]
			new_cell = [c1, new_row, c2, r2]
		else:
			return

		rows.append(new_row)
		rows = list(set(rows))
		cols.append(new_col)
		cols = list(set(cols))
		rows.sort()
		cols.sort()
		value_cells.append(old_cell)
		value_cells.append(new_cell)
		coord_cells = []
		for c1, r1, c2, r2 in value_cells:
			x1, y1, x2, y2 = cols.index(c1), rows.index(r1), cols.index(c2), rows.index(r2)
			coord_cells.append([x1, y1, x2, y2])
		# sort by Y first then X
		coord_cells.sort(key=lambda c: c[Y_MIN] * 100 + c[X_MIN])

		layout = {
			"rows": rows,
			"cols": cols,
			"cells": coord_cells
		}
		self.fixed_set_layout(layout)

	def destroy_pane(self, group):
		layout = self.layout
		cells = layout['cells']
		try:
			x1, y1, x2, y2 = cells.pop(group)
		except:
			return
		adjacent_cells = self.get_adjacent_cells(group)
		adjacent_cells['left'].sort(key=lambda c: c[Y_MIN])
		adjacent_cells['right'].sort(key=lambda c: c[Y_MIN])
		adjacent_cells['up'].sort(key=lambda c: c[X_MIN])
		adjacent_cells['down'].sort(key=lambda c: c[X_MIN])

		extend_direction = None
		for dir, cs in adjacent_cells.items():
			if not cs:
				continue
			if ((y1 == cs[0][Y_MIN] and y2 == cs[-1][Y_MAX]) or
					(x1 == cs[0][X_MIN] and x2 == cs[-1][X_MAX])):
				extend_direction = dir

		if not extend_direction:
			return
		for extend_cell in adjacent_cells[extend_direction]:
			try:
				i = cells.index(extend_cell)
			except:
				continue
			if extend_direction == 'left':
				cells[i][X_MAX] = x2
			elif extend_direction == 'right':
				cells[i][X_MIN] = x1
			elif extend_direction == 'up':
				cells[i][Y_MAX] = y2
			elif extend_direction == 'down':
				cells[i][Y_MIN] = y1

		layout['cells'] = cells
		self.fixed_set_layout(layout)

	def get_closest_group(self, direction):
		adjacent_cells = self.get_adjacent_cells(self.current_group)
		try:
			group = self.cells.index(adjacent_cells[direction][0])
		except:
			group = -1
		return group

	def move_to_pane(self, direction):
		group = self.get_closest_group(direction)
		if group == -1:
			return
		self.fixed_focus_group(group)

	def carry_file_to_pane(self, direction):
		group = self.get_closest_group(direction)
		view = self.window.active_view()
		if not (view and group >= 0):
			return
		self.window.set_view_index(view, group, 0)
		self.fixed_focus_group(group)

	def clone_file_to_pane(self, direction):
		view = self.window.active_view()
		self.window.run_command("clone_file")
		self.carry_file_to_pane(direction)
		self.window.focus_view(view)

	def get_options(self, command):
		command = command.lower()
		if 'v' in command:
			pattern = 'v'
		elif 'h' in command:
			pattern = 'h'
		else:
			raise Exception(': Invalid command string' % PLUGIN_NAME)
		i = command.find(pattern)
		group = int(command[:i] or self.current_group)
		scale = int(command[i + 1:] or 50) / 100
		return group, pattern, scale


class DebugCommand(PaneCommand):
	def run(self):
		sublime.log_commands(True)
		self.split_pane(0, 'h', 0.8)
		self.split_pane(0, 'v', 0.5)
		self.split_pane(1, 'h', 0.3)
		self.split_pane(3, 'v', 0.3)
		self.split_pane(4, 'v', 0.8)


class MoveToPaneCommand(PaneCommand):
	def run(self, direction):
		self.move_to_pane(direction)


class CycleBetweenPanesCommand(PaneCommand):
	def run(self):
		num_groups = self.window.num_groups()
		next_group = self.current_group + 1
		if next_group > num_groups - 1:
			next_group = 0
		self.fixed_focus_group(next_group)


class ReverseCycleBetweenPanesCommand(PaneCommand):
	def run(self):
		num_groups = self.window.num_groups()
		prev_group = self.current_group - 1
		if prev_group < 0:
			prev_group = num_groups - 1
		self.fixed_focus_group(prev_group)


class SplitPaneCommand(PaneCommand):
	def run(self, commands, files=[]):
		for command in commands:
			group, pattern, scale = self.get_options(command)
			self.split_pane(group, pattern, scale)


class CombineAllPanesCommand(PaneCommand):
	def run(self):
		self.fixed_set_layout({
			'rows': [0, 1],
			'cols': [0, 1],
			'cells': [[0, 0, 1, 1]]
		})


class DestroyCurrentPaneCommand(PaneCommand):
	def run(self):
		self.destroy_pane(self.current_group)


class CloneFileToPaneCommand(PaneCommand):
	def run(self, direction):
		self.clone_file_to_pane(direction)


class CarryFileToPaneCommand(PaneCommand):
	def run(self, direction):
		self.carry_file_to_pane(direction)


class LoadLayoutCommand(PaneCommand):
	def run(self):
		# TODO
		pass


class SaveLayoutCommand(PaneCommand):
	def run(self):
		# TODO
		pass


class UndoLayoutCommand(PaneCommand):
	def run(self):
		self.undo_layout()
