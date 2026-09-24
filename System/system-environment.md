# System Environment

## `.bashrc`

```
# Find and edit
find . -name "$1" -exec vim {} \;

```

## `.inputrc`

- Complete folder name input with one **TAB** press.
  A symbolic link requires double **TAB** press to input folder name and `/`. Change the GNU Readline configuration to enable single press completion.
  
  ```
  set mark-symlinked-directories on
  ```
  
  Let shell reload the configuration

  ```
  bind -f ~/.inputrc
  ```
