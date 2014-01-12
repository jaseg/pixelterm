PIXELTERM
=========
A utility to render pixely images on your terminal. Now also with animated GIF
support*.

![animated example](https://raw.github.com/jaseg/pixelterm/master/example.gif)
![example](https://raw.github.com/jaseg/pixelterm/master/example.png)

*for best results, use tmux (for some reason that reduces flickering)

Installation
-----------
Although there is a ``setup.py`` I have grown quite frustrated with setuptools
and pythons abysmal package handling. Any contributions are welcome.

Usage
-----
```
pixelterm FILE
gifterm FILE
```

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
That awesome Rainbow Dash is by [starsteppony on
deviantart](http://starsteppony.deviantart.com/art/Rainbow-Dash-Salute-263753912).
Credit for pop tart cat/nyan cat goes to [prguitarman from
tumblr](http://prguitarman.tumblr.com/post/4281177195/pop-tart-cat-icon-can-be-found-here).

