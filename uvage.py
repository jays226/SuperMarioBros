# A library file for simplifying pygame interaction.  You MUST place this file in the same directory as your game py files.

'''This code is the original work of Luther Tychonievich, who releases it
into the public domain.

As a courtesy, Luther would appreciate it if you acknowledged him in any work
that benefited from this code.

Edits, removals, and additions made by Adam Dirting under the supervision of Raymond Pettit.
'''

from __future__ import division # only used in python2


import pygame, sys
import urllib, os.path

if 'urlretrieve' not in dir(urllib): # python 3
    from urllib.request import urlretrieve as _urlretrieve
else: # python 2
    raise Exception("UVaGE detected Python 2 as the main interperter, make sure you are running UVaGE with the latest version of Python")
    # _urlretrieve = urllib.urlretrieve

pygame.init()

# a cache to avoid loading images many time
_known_images = {}

def _image(key, flip=False, w=0, h=0, angle=0):
    '''A method for loading images, caching them, and flipping them'''
    if '__hash__' not in dir(key):
        key = id(key)
    angle,w,h = int(angle), int(w), int(h)
    ans = None
    if (key,flip,w,h,angle) in _known_images:
        ans = _known_images[(key,flip,w,h,angle)]
    elif angle != 0:
        base = _image(key,flip,w,h)
        img = pygame.transform.rotozoom(base, angle, 1)
        _known_images[(key,flip,w,h,angle)] = img
        ans = img
    elif  w != 0 or h != 0:
        base = _image(key, flip)
        img = pygame.transform.smoothscale(base, (w,h))
        _known_images[(key,flip,w,h,angle)] = img
        ans = img
    elif flip:
        base = _image(key)
        img = pygame.transform.flip(base, True, False)
        _known_images[(key,flip,w,h,angle)] = img
        ans = img
    else:
        img, _ = _get_image(key)
        _known_images[(key,flip,w,h,angle)] = img
        ans = img
    if w == 0 and h == 0:
        if angle != 0: tmp = _image(key, flip, w, h)
        else: tmp = ans
        _known_images[(key,flip,tmp.get_width(),tmp.get_height(), angle)] = ans
    return ans
    
def _image_from_url(url):
    '''a method for loading images from urls by first saving them locally'''
    filename = os.path.basename(url)
    if not os.path.exists(filename):
        if '://' not in url: url = 'http://'+url
        _urlretrieve(url, filename)
    image, filename =_image_from_file(filename)
    return image, filename

def _image_from_file(filename):
    '''a method for loading images from files'''
    image = pygame.image.load(filename).convert_alpha()
    _known_images[filename] = image
    _known_images[(image.get_width(), image.get_height(), filename)] = image
    return image, filename

def _get_image(thing):
    '''a method for loading images from cache, then file, then url'''
    if thing in _known_images: return _known_images[thing], thing
    sid = '__id__'+str(id(thing))
    if sid in _known_images: return _known_images[sid], sid
    try:
        if type(thing) is str:
            if os.path.exists(thing): return _image_from_file(thing)
            return _image_from_url(thing)
    except:
        exit("An error occured while fetching image, are you sure the file/website name is \"" + thing + "\"?")

    _known_images[sid] = thing
    _known_images[(thing.get_width(), thing.get_height(), sid)] = thing
    return thing, sid

def load_sprite_sheet(url_or_filename, rows, columns):
    '''Loads a sprite sheet. Assumes the sheet has rows-by-columns evenly-spaced images and returns a list of those images.'''
    sheet, key = _get_image(url_or_filename)
    height = sheet.get_height() / rows
    width = sheet.get_width() / columns
    frames = []
    for row in range(rows):
        for col in range(columns):
            clip = pygame.Rect( col*width, row*height, width, height )
            frame = sheet.subsurface(clip)
            frames.append(frame)
    return frames
__all__ = ['load_sprite_sheet']

def from_image(x, y, filename_or_url):
    '''Creates a SpriteBox object at the given location from the provided filename or url'''
    image, key = _get_image(filename_or_url)
    return SpriteBox(x, y, image, None)
__all__.append('from_image')

def from_color(x, y, color, width, height):
    '''Creates a SpriteBox object at the given location with the given color, width, and height'''
    return SpriteBox(x, y, None, color, width, height)
__all__.append('from_color')

def from_circle(x, y, color, radius, *args):
    '''Creates a SpriteBox object at the given location filled with a circle.
    from_circle(x,y,color,radius,color2,radius2,color3,radius3,...) works too; the largest circle must come first'''
    img = pygame.surface.Surface((radius*2, radius*2), pygame.SRCALPHA, 32)
    if type(color) is str: color = pygame.Color(color)
    pygame.draw.circle(img, color, (radius,radius), radius)
    for i in range(1, len(args), 2):
        color = args[i-1]
        if type(color) is str: color = pygame.Color(color)
        pygame.draw.circle(img, color, (radius,radius), args[i])
    return SpriteBox(x, y, img, None)

def from_polygon(x, y, color, *pts):
    '''Creates a SpriteBox of minimal size to store the given points.
    Note that it will be centered; adding the same offset to all points does not change the polygon.'''
    x0 = min(x for x,y in pts)
    y0 = min(y for x,y in pts)
    w = max(x for x,y in pts) - x0
    h = max(y for x,y in pts) - y0
    img = pygame.surface.Surface((w,h), pygame.SRCALPHA, 32)
    if type(color) is str: color = pygame.Color(color)
    pygame.draw.polygon(img, color, [(x-x0,y-y0) for x,y in pts])
    return SpriteBox(x, y, img, None)

def from_text(x, y, text, fontsize, color, bold=False, italic=False):
    '''Creates a SpriteBox object at the given location with the given text as its content'''
    # always use default font. Earlier versions allowed others, but this proved platform-dependent
    font = pygame.font.Font(None, fontsize)
    font.set_bold(bold)
    font.set_italic(italic)
    if type(color) is str: color = pygame.Color(color)
    return from_image(x,y,font.render(text,True,color))
__all__.append('from_text')

class Camera(object):
    '''A camera defines what is visible. It has a width, height, full screen status,
    and can be moved. Moving a camera changes what is visible.
    '''
    is_initialized = False
#    __slots__ = ["_surface", "x", "y", "speedx", "speedy"]
    def __init__(self, width, height, full_screen=False):
        '''Camera(pixelsWide, pixelsTall, False) makes a window; using True instead makes a full-screen display.'''
        if Camera.is_initialized: raise Exception("You can only have one Camera at a time")
        # if height > 768: raise Exception("The Game Expo screens will only be 768 pixels tall")
        # if width > 1366: raise Exception("The Game Expo screens will only be 1366 pixels wide")
        if full_screen:
            self.__dict__['_surface'] = pygame.display.set_mode([width, height], pygame.FULLSCREEN)
        else:
            self.__dict__['_surface'] = pygame.display.set_mode([width, height])
        self.__dict__['_x'] = 0
        self.__dict__['_y'] = 0
        Camera.is_initialized = True
    def move(self, x, y=None):
        '''camera.move(3, -7) moves the screen's center to be 3 more pixels to the right and 7 more up'''
        if y is None: x, y = x
        self.x += x
        self.y += y
    def draw(self, thing, *args):
        '''camera.draw(box) draws the provided SpriteBox object
        camera.draw(image, x, y) draws the provided image centered at the provided coordinates
        camera.draw("Hi", 12, "red", x, y) draws the text Hi in a red 12-point font at x,y'''
        if isinstance(thing, SpriteBox):
            thing.draw(self)
        elif isinstance(thing, pygame.Surface):
            try:
                if len(args) == 1: x,y = args[0]
                else: x,y = args[:2]
                self._surface.blit(thing, [x-thing.get_width()/2,y-thing.get_height()/2])
                ok = True
            except BaseException as e:
                ok = False
            if not ok:
                raise Exception("Wrong arguments; try .draw(surface, [x,y])")
        elif type(thing) is str:
            try:
                size = args[0]
                color = args[1]
                if type(color) is str: color = pygame.Color(color)
                self.draw(pygame.font.Font(None,size).render(thing,True,color), *args[2:])
                ok = True
            except BaseException as e:
                ok = False
            if not ok:
                raise Exception("Wrong arguments; try .draw(text, fontSize, color, [x,y])", e)
        else:
            raise Exception("I don't know how to draw a ",type(thing))

    def display(self):
        '''Causes what has been drawn recently by calls to draw(...) to be displayed on the screen'''
        pygame.display.flip()
    def clear(self, color):
        '''Erases the screen by filling it with the given color'''
        if type(color) is str: color = pygame.Color(color)
        self._surface.fill(color)
    def __getattr__(self, name):
        if name in self.__dict__: return self.__dict__[name]
        x, y, w, h = self._x, self._y, self._surface.get_width(), self._surface.get_height()
        if name == 'left': return x
        if name == 'right': return x + w
        if name == 'top': return y
        if name == 'bottom': return y + h
        if name == 'x': return x + w/2
        if name == 'y': return y + h/2
        if name == 'center': return x+w/2, y+h/2
        if name == 'topleft': return x,y
        if name == 'topright': return x + w, y
        if name == 'bottomleft': return x, y + h
        if name == 'bottomright': return x + w, y + h
        if name == 'width': return w
        if name == 'height': return h
        if name == 'size': return w, h
        if name == 'mousex': return pygame.mouse.get_pos()[0] + self._x
        if name == 'mousey': return pygame.mouse.get_pos()[1] + self._y
        if name == 'mouse': return pygame.mouse.get_pos()[0] + self._x, pygame.mouse.get_pos()[1] + self._y
        if name == 'mouseclick': return any(pygame.mouse.get_pressed())
        raise Exception("There is no '" + name + "' in a Camera object")

    def __setattr__(self, name, value):
        if name in self.__dict__:
            self.__dict__[name] = value
            return
        w, h = self._surface.get_width(), self._surface.get_height()
        if name == 'left': self._x = value
        elif name == 'right': self._x = value - w
        elif name == 'top': self._y = value
        elif name == 'bottom': self._y = value - h
        elif name == 'x': self._x = value-w/2
        elif name == 'y': self._y = value-h/2
        elif name == 'center': self._x, self._y = value[0]-w/2, value[1]-h/2
        elif name == 'topleft': self._x, self._y = value[0], value[1]
        elif name == 'topright': self._x, self._y = value[0] - w, value[1]
        elif name == 'bottomleft': self._x, self._y = value[0], value[1] - h
        elif name == 'bottomright': self._x, self._y = value[0] - w, value[1] - h
        elif name in ['width','height','size','mouse','mousex','mousey','mouseclick']:
            raise Exception("You cannot change the '" + name + "' of a Camera object")
        else:
            sys.stderr.write("INFO: added \""+name+"\" to camera")
            self.__dict__[name] = value
    def __repr__(self):
        return str(self)

    def __str__(self):
        return '%dx%d Camera centered at %d,%d' % (self.width, self.height, self.x, self.y)

__all__.append('Camera')



class SpriteBox(object):
    '''Intended to represent a sprite (i.e., an image that can be drawn as part of a larger view) and the box that contains it. Has various collision and movement methods built in.'''
#    __slots__ = ["x","y","speedx","speedy","_w","_h","_key","_image","_color"]
    def __init__(self, x, y, image, color, w=None, h=None):
        '''You should probably use the from_image, from_text, or from_color method instead of this one'''
        self.__dict__['x'] = x
        self.__dict__['y'] = y
        self.__dict__['speedx'] = 0
        self.__dict__['speedy'] = 0
        if image is not None:
            self._set_key(image, False, 0, 0, 0)
            if w is not None:
                if h is not None: self.size = w,h
                else: self.width = w
            elif h is not None: self.height = h
        elif color is not None:
            if w is None or h is None: raise Exception("must supply size of color box")
            self.__dict__['_key'] = None
            self.__dict__['_image'] = None
            self.__dict__['_w'] = w
            self.__dict__['_h'] = h
            self.color = color
        pass
        
    def _set_key(self, name, flip, width, height, angle):
        width = int(width+0.5)
        height = int(height+0.5)
        angle = ((int(angle)%360)+360)%360
        unrot = _image(name, flip, width, height)
        if width == 0 and height == 0: 
            width = unrot.get_width()
            height = unrot.get_height()
        self.__dict__['_key'] = (name, flip, width, height, angle)
        self.__dict__['_image'] = _image(*self.__dict__['_key'])
        self.__dict__['_color'] = None
        self.__dict__['_w'] = self.__dict__['_image'].get_width()
        self.__dict__['_h'] = self.__dict__['_image'].get_height()
        

    def __getattr__(self, name):
        x, y, w, h = self.x, self.y, self._w, self._h
        if name == 'xspeed': name = 'speedx'
        if name == 'yspeed': name = 'speedy'
        if name == 'left': return x - w / 2
        if name == 'right': return x + w / 2
        if name == 'top': return y - h / 2
        if name == 'bottom': return y + h / 2
        if name == 'center': return x, y
        if name == 'topleft': return x - w / 2, y - h / 2
        if name == 'topright': return x + w / 2, y - h / 2
        if name == 'bottomleft': return x - w / 2, y + h / 2
        if name == 'bottomright': return x + w / 2, y + h / 2
        if name == 'width': return w
        if name == 'height': return h
        if name == 'width': return w
        if name == 'height': return h
        if name == 'size': return w, h
        if name == 'speed': return self.speedx, self.speedy
        if name == 'rect': return pygame.Rect(self.topleft, self.size)
        if name == 'image': return self.__dict__['_image']
        if name in self.__dict__:
            return self.__dict__[name]
        raise Exception("There is no '" + name + "' in a SpriteBox object")

    def __setattr__(self, name, value):
        w, h = self._w, self._h
        if name == 'xspeed': name = 'speedx'
        if name == 'yspeed': name = 'speedy'
        if name in self.__dict__:
            self.__dict__[name] = value
        elif name == 'left': self.x = value + w / 2
        elif name == 'right': self.x = value - w / 2
        elif name == 'top': self.y = value + h / 2
        elif name == 'bottom': self.y = value - h / 2
        elif name == 'center': self.x, self.y = value[0], value[1]
        elif name == 'topleft': self.x, self.y = value[0] + w / 2, value[1] + h / 2
        elif name == 'topright': self.x, self.y = value[0] - w / 2, value[1] + h / 2
        elif name == 'bottomleft': self.x, self.y = value[0] + w / 2, value[1] - h / 2
        elif name == 'bottomright': self.x, self.y = value[0] - w / 2, value[1] - h / 2
        elif name == 'width': self.scale_by(value/w)
        elif name == 'height': self.scale_by(value/h)
        elif name == 'size': 
            if self.__dict__['_image'] is not None:
                key = self.__dict__['_key']
                self._set_key(key[0], key[1], value[0], value[1], key[4])
            else:
                self.__dict__['_w'] = value[0]
                self.__dict__['_h'] = value[1]
        elif name == 'speed': self.speedx, self.speedy = value[0], value[1]
        elif name == 'color':
            self.__dict__['_image'] = None
            self.__dict__['_key'] = None
            if type(value) is str: value = pygame.Color(value)
            self.__dict__['_color'] = value
        elif name == 'image':
            self.__dict__['_color'] = None
            if self.__dict__['_key'] is None:
                self._set_key(value, False, w, h, 0)
            else:
                key = self.__dict__['_key']
                self._set_key(value, *key[1:])
        else:
            sys.stderr.write("INFO: added \""+name+"\" to box")
            self.__dict__[name] = value

    def overlap(self, other, padding=0, padding2=None):
        '''b1.overlap(b1) returns a list of 2 values such that self.move(result) will cause them to not overlap
        Returns [0,0] if there is no overlap (i.e., if b1.touches(b2) returns False
        b1.overlap(b2, 5) adds a 5-pixel padding to b1 before computing the overlap
        b1.overlap(b2, 5, 10) adds a 5-pixel padding in x and a 10-pixel padding in y before computing the overlap'''
        if padding2 is None: padding2 = padding
        l = other.left - self.right - padding
        r = self.left - other.right - padding
        t = other.top - self.bottom - padding2
        b = self.top - other.bottom - padding2
        m = max(l, r, t, b)
        if m >= 0: return [0, 0]
        elif m == l: return [l, 0]
        elif m == r: return [-r, 0]
        elif m == t: return [0, t]
        else: return [0, -b]

    def touches(self, other, padding=0, padding2=None):
        '''b1.touches(b1) returns True if the two SpriteBoxes overlap, False if they do not
        b1.touches(b2, 5) adds a 5-pixel padding to b1 before computing the touch
        b1.touches(b2, 5, 10) adds a 5-pixel padding in x and a 10-pixel padding in y before computing the touch'''
        if padding2 is None: padding2 = padding
        l = other.left - self.right - padding
        r = self.left - other.right - padding
        t = other.top - self.bottom - padding2
        b = self.top - other.bottom - padding2
        return max(l,r,t,b) <= 0

    def bottom_touches(self, other, padding=0, padding2=None):
        '''b1.bottom_touches(b2) returns True if both b1.touches(b2) and b1's bottom edge is the one causing the overlap.'''
        if padding2 is None: padding2 = padding
        return self.overlap(other,padding+1,padding2+1)[1] < 0

    def top_touches(self, other, padding=0, padding2=None):
        '''b1.top_touches(b2) returns True if both b1.touches(b2) and b1's top edge is the one causing the overlap.'''
        if padding2 is None: padding2 = padding
        return self.overlap(other,padding+1,padding2+1)[1] > 0

    def left_touches(self, other, padding=0, padding2=None):
        '''b1.left_touches(b2) returns True if both b1.touches(b2) and b1's left edge is the one causing the overlap.'''
        if padding2 is None: padding2 = padding
        return self.overlap(other,padding+1,padding2+1)[0] > 0

    def right_touches(self, other, padding=0, padding2=None):
        '''b1.right_touches(b2) returns True if both b1.touches(b2) and b1's right edge is the one causing the overlap.'''
        if padding2 is None: padding2 = padding
        return self.overlap(other,padding+1,padding2+1)[0] < 0

    def contains(self, x, y=None):
        '''checks if the given point is inside this SpriteBox's bounds or not'''
        if y is None: x,y = x
        return abs(x-self.x)*2 < self._w and abs(y-self.y)*2 < self._h

    def move_to_stop_overlapping(self, other, padding=0, padding2=None):
        '''b1.move_to_stop_overlapping(b2) makes the minimal change to b1's position necessary so that they no longer overlap'''
        o = self.overlap(other,padding, padding2)
        if o != [0,0]:
            self.move(o)
            if o[0] * self.speedx < 0: self.speedx = 0
            if o[1] * self.speedy < 0: self.speedy = 0
    def move_both_to_stop_overlapping(self, other, padding=0, padding2=None):
        '''b1.move_both_to_stop_overlapping(b2) changes both b1 and b2's positions so that they no longer overlap'''
        o = self.overlap(other,padding, padding2)
        if o != [0,0]:
            self.move(o[0]/2,o[1]/2)
            other.move(-o[0]/2,-o[1]/2)
            if o[0] != 0:
                self.speedx = (self.speedx+other.speedx)/2
                other.speedx = self.speedx
            if o[1] != 0:
                self.speedy = (self.speedy+other.speedy)/2
                other.speedy = self.speedy


    def move(self, x, y=None):
        '''change position by the given amount in x and y. If only x given, assumed to be a point [x,y]'''
        if y is None: x, y = x
        self.x += x
        self.y += y

    def move_speed(self):
        '''change position by the current speed field of the SpriteBox object'''
        self.move(self.speedx, self.speedy)

    def full_size(self):
        '''change size of this SpriteBox to be the original size of the source image'''
        if self.__dict__['_key'] is None: return
        key = self.__dict__['_key']
        self._set_key(key[0],key[1],0,0,key[4])

    def __repr__(self):
        return str(self)

    def __str__(self):
        return '%dx%d SpriteBox centered at %d,%d' % (self._w, self._h, self.x, self.y)

    def copy_at(self, newx, newy):
        '''Make a new SpriteBox just like this one but at the given location instead of here'''
        return SpriteBox(newx, newy, self._image, self._color, self._w, self._h)
    def copy(self):
        '''Make a new SpriteBox just like this one and in the same location'''
        return self.copy_at(self.x, self.y)

    def scale_by(self, multiplier):
        '''Change the size of this SpriteBox by the given factor
        b1.scale_by(1) does nothing; b1.scale_by(0.4) makes b1 40% of its original width and height.'''
        if self.__dict__['_key'] is None:
            self._w *= multiplier
            self._h *= multiplier
        else:
            key = self.__dict__['_key']
            self._set_key(key[0], key[1], key[2]*multiplier, key[3]*multiplier, key[4])

    def draw(self, surface):
        '''b1.draw(camera) is the same as saying camera.draw(b1)
        b1.draw(image) draws a copy of b1 on the image proivided'''
        if isinstance(surface, Camera):
            if self.__dict__['_color'] is not None:
                region = self.rect.move(-surface._x, -surface._y)
                region = region.clip(surface._surface.get_rect())
                surface._surface.fill(self._color, region)
            elif self.__dict__['_image'] is not None:
                surface._surface.blit(self._image, [self.left - surface._x, self.top - surface._y])
        else:
            if self.__dict__['_color'] is not None:
                surface.fill(self._color, self.rect)
            elif self.__dict__['_image'] is not None:
                surface.blit(self._image, self.topleft)
    def flip(self):
        '''mirrors the SpriteBox left-to-right. 
        Mirroring top-to-bottom can be accomplished by
            b1.rotate(180)
            b1.flip()'''
        if self.__dict__['_key'] is None: return
        key = self.__dict__['_key']
        self._set_key(key[0], not key[1], *key[2:])
        
    def rotate(self, angle):
        '''Rotates the SpriteBox by the given angle (in degrees).'''
        if self.__dict__['_key'] is None: return
        key = self.__dict__['_key']
        self._set_key(key[0], key[1], key[2], key[3], key[4]+angle)

__all__.append('SpriteBox')

# a set containing all keys being pressed at a user at any given time
keys = set([])

def is_pressing(key):
    '''Returns a boolean that represents whether the given computer key is being pressed.'''
    global keys
    if key not in key_constants:
        raise KeyError("Key name " + key + " is not a valid key name.")
    elif key_constants[key] in keys:
        return True
    else:
        return False

_timeron = False
_timerfps = 0

def timer_loop(fps, callback, limit=None):
    '''Requests that pygame call the provided function fps times a second
    fps: a number between 1 and 60
    callback: a function that accepts a set of keys pressed since the last tick
    limit: if given, will only run for that many fames and then return True
    returns: True if given limit and limit reached; False otherwise
    ---- edit: keys is no longer passed to the callback function
    seconds = 0
    def tick(keys):
        seconds += 1/30
        if pygame.K_DOWN in keys:
            print 'down arrow pressed'
        if not keys:
            print 'no keys were pressed since the last tick'
        camera.draw(box)
        camera.display()
    
    gamebox.timer_loop(30, tick)
    ----'''
    global _timeron, _timerfps, keys
    # keys = set([])
    if fps > 60: fps = 60
    _timerfps = fps
    _timeron = True
    frames = 0
    pygame.time.set_timer(pygame.USEREVENT, int(1000/fps))
    while not limit or frames < limit:
        event = pygame.event.wait()
        if event.type == pygame.QUIT: break
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE: break
        if event.type == pygame.KEYDOWN:
            keys.add(event.key)
        if event.type == pygame.KEYUP and event.key in keys:
            keys.remove(event.key)
        if event.type == pygame.USEREVENT:
            frames += 1
            pygame.event.clear(pygame.USEREVENT)
            callback()
            # callback(keys)
    pygame.time.set_timer(pygame.USEREVENT, 0)
    _timeron = False
    return limit == frames

def stop_loop():
    '''Completely quits one timer_loop or keys_loop, usually ending the program'''
    pygame.event.post(pygame.event.Event(pygame.QUIT))

__all__.append('stop_loop')


def keys_loop(callback):
    '''Requests that pygame call the provided function each time a key is pressed
    callback: a function that accepts the key pressed
    ----
    def onPress(key):
        if pygame.K_DOWN == key:
            print 'down arrow pressed'
        if pygame.K_a in keys:
            print 'A key pressed'
        camera.draw(box)
        camera.display()
    
    gamebox.keys_loop(onPress)
    ----'''
    while True:
        event = pygame.event.wait()
        if event.type == pygame.QUIT: break
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE: break
        if event.type == pygame.KEYDOWN:
            callback([event.key])
        if event.type == pygame.MOUSEBUTTONDOWN:
            callback([])


__all__.append('keys_loop')


key_constants = { "backspace" : pygame.K_BACKSPACE, "tab" : pygame.K_TAB, "clear" : pygame.K_CLEAR,
                  "return" : pygame.K_RETURN, "pause" : pygame.K_PAUSE, "escape" : pygame.K_ESCAPE,
                  "space" : pygame.K_SPACE, "exclaim" : pygame.K_EXCLAIM, "quotedbl" : pygame.K_QUOTEDBL,
                  "hash" : pygame.K_HASH, "dollar" : pygame.K_DOLLAR, "ampersand" : pygame.K_AMPERSAND,
                  "quote" : pygame.K_QUOTE, "left parenthesis" : pygame.K_LEFTPAREN,
                  "right parenthesis" : pygame.K_RIGHTPAREN, "asterisk" : pygame.K_ASTERISK,
                  "plus sign" : pygame.K_PLUS, "comma" : pygame.K_COMMA, "minus sign" : pygame.K_MINUS,
                  "period" : pygame.K_PERIOD, "forward slash" : pygame.K_SLASH, "0" : pygame.K_0, "1" : pygame.K_1,
                  "2" : pygame.K_2, "3" : pygame.K_3, "4" : pygame.K_4, "5" : pygame.K_5, "6" : pygame.K_6,
                  "7" : pygame.K_7, "8" : pygame.K_8, "9" : pygame.K_9, "colon" : pygame.K_COLON,
                  "semicolon" : pygame.K_SEMICOLON, "less-than sign" : pygame.K_LESS, "equals sign" : pygame.K_EQUALS,
                  "greater-than sign" : pygame.K_GREATER, "question mark" : pygame.K_QUESTION, "at" : pygame.K_AT,
                  "left bracket" : pygame.K_LEFTBRACKET, "backslash" : pygame.K_BACKSLASH,
                  "right bracket" : pygame.K_RIGHTBRACKET, "caret" : pygame.K_CARET, "underscore" : pygame.K_UNDERSCORE,
                  "grave" : pygame.K_BACKQUOTE, "a" : pygame.K_a, "b" : pygame.K_b, "c" : pygame.K_c, "d" : pygame.K_d,
                  "e" : pygame.K_e, "f" : pygame.K_f, "g" : pygame.K_g, "h" : pygame.K_h, "i" : pygame.K_i,
                  "j" : pygame.K_j, "k" : pygame.K_k, "l" : pygame.K_l, "m" : pygame.K_m, "n" : pygame.K_n,
                  "o" : pygame.K_o, "p" : pygame.K_p, "q" : pygame.K_q, "r" : pygame.K_r, "s" : pygame.K_s,
                  "t" : pygame.K_t, "u" : pygame.K_u, "v" : pygame.K_v, "w" : pygame.K_w, "x" : pygame.K_x,
                  "y" : pygame.K_y, "z" : pygame.K_z, "delete" : pygame.K_DELETE, "keypad 0" : pygame.K_KP0,
                  "keypad 1" : pygame.K_KP1, "keypad 2" : pygame.K_KP2, "keypad 3" : pygame.K_KP3,
                  "keypad 4" : pygame.K_KP4, "keypad 5" : pygame.K_KP5, "keypad 6" : pygame.K_KP6,
                  "keypad 7" : pygame.K_KP7, "keypad 8" : pygame.K_KP8, "keypad 9" : pygame.K_KP9,
                  "keypad period" : pygame.K_KP_PERIOD, "keypad divide" : pygame.K_KP_DIVIDE,
                  "keypad multiply" : pygame.K_KP_MULTIPLY, "keypad minus" : pygame.K_KP_MINUS,
                  "keypad plus" : pygame.K_KP_PLUS, "keypad enter" : pygame.K_KP_ENTER,
                  "keypad equals" : pygame.K_KP_EQUALS, "up arrow" : pygame.K_UP, "down arrow" : pygame.K_DOWN,
                  "right arrow" : pygame.K_RIGHT, "left arrow" : pygame.K_LEFT, "insert" : pygame.K_INSERT,
                  "home" : pygame.K_HOME, "end" : pygame.K_END, "page up" : pygame.K_PAGEUP,
                  "page down" : pygame.K_PAGEDOWN, "F1" : pygame.K_F1, "F2" : pygame.K_F2, "F3" : pygame.K_F3,
                  "F4" : pygame.K_F4, "F5" : pygame.K_F5, "F6" : pygame.K_F6, "F7" : pygame.K_F7, "F8" : pygame.K_F8,
                  "F9" : pygame.K_F9, "F10" : pygame.K_F10, "F11" : pygame.K_F11, "F12" : pygame.K_F12,
                  "F13" : pygame.K_F13, "F14" : pygame.K_F14, "F15" : pygame.K_F15, "numlock" : pygame.K_NUMLOCK,
                  "capslock" : pygame.K_CAPSLOCK, "scrollock" : pygame.K_SCROLLOCK, "right shift" : pygame.K_RSHIFT,
                  "left shift" : pygame.K_LSHIFT, "right control" : pygame.K_RCTRL, "left control" : pygame.K_LCTRL,
                  "right alt" : pygame.K_RALT, "left alt" : pygame.K_LALT, "right meta" : pygame.K_RMETA,
                  "left meta" : pygame.K_LMETA, "left Windows key" : pygame.K_LSUPER,
                  "right Windows key" : pygame.K_RSUPER, "mode shift" : pygame.K_MODE, "help" : pygame.K_HELP,
                  "print screen" : pygame.K_PRINT, "sysrq" : pygame.K_SYSREQ, "break" : pygame.K_BREAK,
                  "menu" : pygame.K_MENU, "power" : pygame.K_POWER, "Euro" : pygame.K_EURO,
                  "Android back button" : pygame.K_AC_BACK}



if __name__ == "__main__":
    camera = Camera(400, 400)

    camera.x = 10

    b = from_text(40,50,"It Works! (type \"0\")",40,"red", italic=True, bold=False)
    b.speedx = 3
    b.left += 2
    b.y = 100
    b.move_speed()

    camera.draw(b)
    camera.display()

    def tick():
        global b
        if keys:
            if pygame.K_0 in keys: b = from_text(40,50,"Type \"1\"",40,"blue", italic=False, bold=False)
            elif pygame.K_1 in keys: b = from_text(40,50,"Type \"2\"",40,"green", italic=True, bold=True)
            elif pygame.K_2 in keys: b = from_text(40,50,"Type \"3\"",40,"white", italic=False, bold=True)
            elif pygame.K_a in keys: stop_loop()
            elif keys: b.image = "https://www.python.org/static/img/python-logo.png"
            b.full_size()
        b.rotate(-5)
        b.center = camera.mouse
        b.bottom = camera.bottom
        camera.draw(b)
        camera.display()
    
    timer_loop(30, tick)
