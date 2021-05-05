import datetime
from PIL import Image, ImageFont, ImageDraw
import requests
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.pyplot as plt
import numpy as np

def deg_to_dms(deg,type):
    if type=='latitude' and deg>=0:
        chr='N'
    elif type=='latitude' and deg<0:
        chr='S'
    if type=='longitude' and deg>=0:
        chr='E'
    elif type=='longitude' and deg<0:
        chr='O'
    deg=abs(deg)
    d = int(deg)
    md = abs(deg - d) * 60
    m = int(md)
    sd = (md - m) * 60
    #return [d, m, sd]       
    return str(d)+"°"+str(m)+"'"+chr

#inky config
WIDTH=212 
HEIGHT=104
WHITE=0
BLACK=1
RED=2

url="http://api.open-notify.org/iss-now.json"
proxy={"http":'http://127.0.0.1:3128'}
response=requests.get(url)#,proxies=proxy)

latitude=float(response.json()['iss_position']['latitude'])
longitude=float(response.json()['iss_position']['longitude'])
now=response.json()['timestamp']

#print("Latitude",latitude)
str_lat=deg_to_dms(latitude,'latitude')
str_lon=deg_to_dms(longitude,'longitude')
#print("Longitude",longitude)
#print(now)

    


fig=plt.figure(figsize=(WIDTH/100, HEIGHT/100),dpi=100)

ax = plt.axes(projection=ccrs.PlateCarree(central_longitude=longitude))
ax.set_extent([longitude-90, longitude+90, latitude-45, latitude+45], crs=ccrs.PlateCarree())
ax.add_feature(cfeature.COASTLINE,linewidth=0.5)
ax.add_feature(cfeature.BORDERS, linewidth=0.5,linestyle=':')

#le point est tracé plus tard dans Pillow
#plt.plot(longitude-longitude, latitude,  markersize=5, marker='o', color='red')
#plt.show()
plt.tight_layout(pad=0.0) # suppression des marges

# conversion en image Pillow
fig.canvas.draw()
img = np.frombuffer(fig.canvas.tostring_rgb(), dtype=np.uint8)#,sep='')
img  = img.reshape(fig.canvas.get_width_height()[::-1] + (3,))
img=Image.frombytes('RGB', fig.canvas.get_width_height(),fig.canvas.tostring_rgb())

#passage en mode palette
img=img.quantize(colors=2) # passage en mode P (si ordre des couleurs pas bon, faire un invert ou changer les param de qr)

# point de l'ISS
draw = ImageDraw.Draw(img)    
draw.ellipse((WIDTH/2-2,HEIGHT/2-2,WIDTH/2+2,HEIGHT/2+2),fill=RED)

#supression des lignes disgracieuses
draw.rectangle((0,0,211,103),fill=None,width=3,outline=WHITE)

#texte date/heure/coord
fontLIB= ImageFont.truetype("/home/pi/Inky-scripts/Ubuntu Nerd Font Complete.ttf", 10)
#fontLIB= ImageFont.truetype("Ubuntu Nerd Font Complete.ttf", 10)
message=datetime.datetime.now().strftime("%d/%m/%Y - %H:%M")+" ["+str_lat+" "+str_lon+"]"
w,h = fontLIB.getsize(message)
draw.rectangle((0, HEIGHT-h, 0 + w, HEIGHT-h + h), fill=WHITE)
draw.text((0,HEIGHT-h),message, BLACK, font=fontLIB)

#display
img.putpalette([255,255,255,0,0,0,255,0,0], rawmode='RGB')
#print(img.size)
#img.show()

from inky.auto import auto
# Set up the display
try:
    inky_display = auto(ask_user=True, verbose=True)
except TypeError:
    raise TypeError("You need to update the Inky library to >= v1.1.0")


if inky_display.resolution not in ((212, 104), (250, 122)):
    w, h = inky_display.resolution
    raise RuntimeError("This example does not support {}x{}".format(w, h))

img = img.transpose(Image.ROTATE_180)
inky_display.set_image(img)
inky_display.show()
