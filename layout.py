import os
import json
import sublime, sublime_plugin


PLUGIN_NAME = 'Layout'
PACKAGES_PATH = sublime.packages_path()
PLUGIN_PATH = os.path.join(PACKAGES_PATH, PLUGIN_NAME)
LAYOUT_PATH = os.path.join(PLUGIN_PATH, 'layouts')

X_MIN, Y_MIN, X_MAX, Y_MAX = (0, 1, 2, 3)


# TODO: remove
from datetime import datetime
def q(*args):
	if args:
		args = [str(arg) for arg in args]
		s = '\t'.join(args)
		s = str(datetime.now()) + '\n\t' + s
	else:
		s = '-' * 80
	with open(os.path.join(PLUGIN_PATH, '_debug.log'), 'a+') as fp:
		fp.write(s + '\n')


def init_environment():
	if not os.path.isdir(LAYOUT_PATH):
		os.mkdir(LAYOUT_PATH)

init_environment()


def Settings():
    return sublime.load_settings('%s.sublime-settings' % PLUGIN_NAME)


class PaneCommand(sublime_plugin.WindowCommand):
	@property
	def layout(self):
		return self.window.get_layout()

	@property
	def cells(self):
		return self.window.get_layout()['cells']

	@property
	def current_group(self):
		return self.window.active_group()

	# TODO: replace
	def get_open_files(self):
		open_files = []
		for i in range(len(self.cells)):
			views = self.window.views_in_group(i)
			open_files.append([])
			for view in views:
				file_path = view.file_name()
				open_files[i].append(file_path)
		return open_files

	def save_layout_to_file(self, filename):
		layout = self.layout
		layout['views'] = []
		layout['active_group'] = self.current_group

		def view_to_jsonable(view):
			return dict(
				file_name=view.file_name(),
				name=view.name(),
				is_read_only=view.is_read_only(),
				is_scratch=view.is_scratch()
			)

		for i in range(len(layout['cells'])):
			views = self.window.views_in_group(i)
			views = [view_to_jsonable(view) for view in views]
			layout['views'].append(views)

		with open(os.path.join(LAYOUT_PATH, '%s.layout' % filename), 'w') as fp:
			fp.write(json.dumps(layout, indent=2))

	# TODO
	def load_layout_from_json(self, data):
		pass

	def fixed_set_layout(self, layout):
		# A bug was introduced in Sublime Text 3, sometime before 3053,
		# in that it changes the active group to 0 when the layout is changed.
		group = min(self.current_group, self.window.num_groups() - 1)
		self.window.set_layout(layout)
		self.fixed_focus_group(group)

	def fixed_focus_group(self, group):
		# I have no idea why this is work instead of
		# `self.window.focus_group(group)`
		sublime.set_timeout(lambda : self.window.focus_group(group), 0)
		sublime.set_timeout(lambda : self.window.focus_group(group), 0)

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

	def layout_to_value_cells(self, layout):
		value_cells = []
		rows = layout['rows']
		cols = layout['cols']
		for x1, y1, x2, y2 in layout['cells']:
			value_cells.append([cols[x1], rows[y1], cols[x2], rows[y2]])
		return value_cells

	def value_cells_to_layout(self, value_cells):
		rows = set()
		cols = set()
		for c1, r1, c2, r2 in value_cells:
			cols.add(c1)
			rows.add(r1)
			cols.add(c2)
			rows.add(r2)
		cols = list(cols)
		rows = list(rows)
		cols.sort()
		rows.sort()

		max_x = 0
		cells = []
		for c1, r1, c2, r2 in value_cells:
			x1, y1, x2, y2 = cols.index(c1), rows.index(r1), cols.index(c2), rows.index(r2)
			cells.append([x1, y1, x2, y2])
			if max_x < x2:
				max_x = x2
		# cells arrange by y1 first then x1
		cells.sort(key=lambda c: c[Y_MIN] * (max_x + 1) + c[X_MIN])

		layout = {
			'cols': cols,
			'rows': rows,
			'cells': cells
		}
		return layout

	def split_pane(self, group, pattern, scale):
		rows = self.layout['rows']
		cols = self.layout['cols']
		coord_cells = self.layout['cells']

		try:
			# (x1, y1) is top left point, (x2, y2) is bottom right point
			x1, y1, x2, y2 = coord_cells.pop(group)
			c1, r1, c2, r2 = cols[x1], rows[y1], cols[x2], rows[y2]
		except:
			return
		value_cells = self.layout_to_value_cells({
			'rows': rows,
			'cols': cols,
			'cells': coord_cells
		})

		# vertical
		if pattern == 'v':
			c = (c2 - c1) * scale + c1
			old_cell = [c1, r1, c, r2]
			new_cell = [c, r1, c2, r2]
		# horizontal
		elif pattern == 'h':
			r = (r2 - r1) * scale + r1
			old_cell = [c1, r1, c2, r]
			new_cell = [c1, r, c2, r2]
		else:
			return

		value_cells.append(old_cell)
		value_cells.append(new_cell)
		layout = self.value_cells_to_layout(value_cells)
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
		# remove extra rulers of column or row and reset cells
		value_cells = self.layout_to_value_cells(layout)
		layout = self.value_cells_to_layout(value_cells)
		# kill all views in pane
		if Settings().get('auto_close_view'):
			self.window.run_command('close')
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


class Recordable(object):
	def do_run(self, *args, **kwargs):
		raise NotImplemented

	@classmethod
	def add_history(cls, item):
		if len(cls.history) > cls.max_history_num:
			cls.history.pop(0)
		cls.history.append(item)

	@classmethod
	def add_redo_history(cls, item):
		if len(cls.redo_history) > cls.max_history_num:
			cls.redo_history.pop(0)
		cls.redo_history.append(item)

	@classmethod
	def next_record(cls):
		item = cls.history.pop()
		cls.add_redo_history(item)
		return item

	@classmethod
	def prev_record(cls):
		item = cls.redo_history.pop()
		cls.add_history(item)
		return item

	@classmethod
	def clear_history(cls):
		cls.history = []
		cls.redo_history = []


class MoveableCommand(PaneCommand, Recordable):
	# history of move between panes
	history = []
	redo_history = []
	max_history_num = Settings().get('max_move_history') or 100

	def run(self, *args, **kwargs):
		self.add_history(self.current_group)
		self.do_run(*args, **kwargs)


class RevocableCommand(PaneCommand, Recordable):
	# history of move between panes
	history = []
	redo_history = []
	max_history_num = Settings().get('max_layout_history') or 10

	def run(self, *args, **kwargs):
		# TODO
		self.history.append(self.window)
		# Clear move history every time
		MoveableCommand.clear_history()
		self.do_run(*args, **kwargs)


class MoveToPaneCommand(MoveableCommand):
	def do_run(self, direction):
		self.move_to_pane(direction)


class CycleBetweenPanesCommand(MoveableCommand):
	def do_run(self):
		num_groups = self.window.num_groups()
		next_group = self.current_group + 1
		if next_group > num_groups - 1:
			next_group = 0
		self.fixed_focus_group(next_group)


class ReverseCycleBetweenPanesCommand(MoveableCommand):
	def do_run(self):
		num_groups = self.window.num_groups()
		prev_group = self.current_group - 1
		if prev_group < 0:
			prev_group = num_groups - 1
		self.fixed_focus_group(prev_group)


class SplitPaneCommand(RevocableCommand):
	def do_run(self, commands):
		for command in commands:
			group, pattern, scale = self.get_options(command)
			self.split_pane(group, pattern, scale)


class CombineAllPanesCommand(RevocableCommand):
	def do_run(self):
		self.fixed_set_layout({
			'rows': [0, 1],
			'cols': [0, 1],
			'cells': [[0, 0, 1, 1]]
		})


class DestroyCurrentPaneCommand(RevocableCommand):
	def do_run(self):
		self.destroy_pane(self.current_group)


class CloneFileToPaneCommand(RevocableCommand):
	def do_run(self, direction):
		self.clone_file_to_pane(direction)


class CarryFileToPaneCommand(RevocableCommand):
	def do_run(self, direction):
		self.carry_file_to_pane(direction)


class LoadLayoutFromCommand(PaneCommand):
	def load_layout_from_file(self, filename):
		data = open(os.path.join(LAYOUT_PATH, filename + '.layout'), 'r').read()
		self.load_layout_from_json(data)

	def run(self, filename=None):
		if filename:
			self.load_layout_from_file(filename)
		else:
			view = self.window.show_input_panel(
				caption='Load from Layout File',
				initial_text='',
				on_done=self.load_layout_from_file,
				on_change=None,
				on_cancel=None
			)
		sublime.status_message('Load from `%s`!' % filename)


class SaveLayoutAsCommand(PaneCommand):
	def run(self, filename=None):
		if filename:
			self.save_layout_to_file(filename)
		else:
			view = self.window.show_input_panel(
				caption='Save as Layout File',
				initial_text='',
				on_done=self.save_layout_to_file,
				on_change=None,
				on_cancel=None
			)
		sublime.status_message('Save to `%s`!' % filename)


class UndoMoveToPaneCommand(PaneCommand):
	def run(self):
		group = MoveableCommand.next_record()
		self.fixed_focus_group(group)


# TODO
class AutoDestroyPane(sublime_plugin.EventListener):
	def on_close(self, view):
		if not Settings().get('auto_destroy_pane'):
			return
		window = view.window()
		q()
		q(window)
		if not window:
			q(window.views())
			# window.run_command('destroy_current_pane')
