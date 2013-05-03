PIXELTERM
=========
A utility to render pixely images on your terminal. Now also with animated GIF
support*.

![example](http://i.imgur.com/Owb3l7l.png)

*for best results, use tmux (for some reason that reduces flickering)

Installation
------------
Type ```sudo make install```, which will copy pixelterm.py to ```/usr/local/bin/pixelterm```.

Usage
-----
```pixelterm FILE```

Advanced usage
--------------
Since I wrote this tool to generate graphics for
[ponysay](https://github.com/jaseg/ponysay), I included a "speech bubble"
feature. To make this tool render speech bubble markers which can later be
parsed by ponysay, color the pixels where these should be placed 50%
transparent red (#FF00007F) for a backward slash link, 50% blue for a forward
slash and a 50% transparent green for the speech bubble. Please note that this
tool converts images two pixel rows at once and these "special" color values
are only parsed for the upper of the two rows. An example image is included.

Credits
-------
That awesome Rainbow Dash is by [starsteppony on deviantart](http://starsteppony.deviantart.com/art/Rainbow-Dash-Salute-263753912)

