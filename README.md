#Layout
A powerful plugin to split window like [tmux](https://github.com/ThomasAdam/tmux) for Sublime Text 3, highly inspired by [Origami](https://github.com/SublimeText/Origami).

![Example](https://raw.githubusercontent.com/loggerhead/Layout/master/artwork/example.gif)

##What can it do?
* Split, resize, destory pane, and move between panes (Yes, same as tmux!)
* Carry or clone current file to pane
* Undo and redo your layout
* Save current layout
* Load layout from file

#Installation
Use [Package Control](https://packagecontrol.io/) :)

#Usage
##Split pane
|   Shortcuts Key    |       Command        |
|--------------------|----------------------|
| `Ctrl+W` `Shift+\` | Split vertically     |
| `Ctrl+W` `-`       | Split horizontally   |
| `Ctrl+W` `3`       | Split to 3 panes     |
| `Ctrl+W` `4`       | Split to 4 panes     |
| `Ctrl+W` `1`       | Merge to 1 pane      |
| `Ctrl+W` `X`       | Destory current pane |

##Move between panes
|   Shortcuts Key    |      Command       |
|--------------------|--------------------|
| `Ctrl+W` `H` | Move to left pane  |
| `Ctrl+W` `L` | Move to right pane |
| `Ctrl+W` `K` | Move to up pane    |
| `Ctrl+W` `J` | Move to down pane  |
| `Ctrl+W` `Tab`     | Move between panes |

##Resize pane
| Shortcuts Key |          Command           |
|---------------|----------------------------|
| `Alt+H`       | Increase pane toward left  |
| `Alt+L`       | Increase pane toward right |
| `Alt+K`       | Increase pane toward up    |
| `Alt+J`       | Increase pane toward down  |

You can hold `Alt` key and press down another key to repeat the command.

##Carry file to pane
|   Shortcuts Key    |         Command          |
|--------------------|--------------------------|
| `Ctrl+W` `Shift+H` | Carry file to left pane  |
| `Ctrl+W` `Shift+L` | Carry file to right pane |
| `Ctrl+W` `Shift+K` | Carry file to up pane    |
| `Ctrl+W` `Shift+J` | Carry file to down pane  |
| `Ctrl+W` `Ctrl+H`  | Clone file to left pane  |
| `Ctrl+W` `Ctrl+L`  | Clone file to right pane |
| `Ctrl+W` `Ctrl+K`  | Clone file to up pane    |
| `Ctrl+W` `Ctrl+J`  | Clone file to down pane  |

##Advance commands
|   Shortcuts Key    |               Command                |
|--------------------|--------------------------------------|
| `Ctrl+W` `S`       | Save current layout to default file  |
| `Ctrl+W` `O`       | Load layout from default file        |
| `Ctrl+W` `Shift+S` | Save current layout to specific file |
| `Ctrl+W` `Shift+R` | Redo layout                          |
| `Ctrl+W` `Shift+Z` | Undo layout                          |


#License
```
            DO WHAT THE FUCK YOU WANT TO PUBLIC LICENSE
                    Version 2, December 2004

 Copyright (C) 2016 Loggerhead <i@loggerhead.me>

 Everyone is permitted to copy and distribute verbatim or modified
 copies of this license document, and changing it is allowed as long
 as the name is changed.

            DO WHAT THE FUCK YOU WANT TO PUBLIC LICENSE
   TERMS AND CONDITIONS FOR COPYING, DISTRIBUTION AND MODIFICATION

  0. You just DO WHAT THE FUCK YOU WANT TO.
```
