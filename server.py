#!/usr/bin/python  

import bottle
import simplejson as json
import os
import time
import wechat_jump_photo

@bottle.route('/sample',method=['GET','POST']) 
def sample():  
    imei = bottle.request.POST.get('imei')
    dt = bottle.request.POST.get('datetime')
    #生成json格式的字符串并返回  
    jsonStr = "{'a':'%s','b':'%s'}" % (imei,dt)
    return jsonStr
    
@bottle.route('/',method=['GET','POST'])  
def indexPage():
  return bottle.static_file('./index.html','./')
  
@bottle.route('/upload',method='POST')  
def getPostParams():
    jsonOb = {'code':'error','msg':'do not run '}
    imgFile = bottle.request.POST.get('imgfile')
    name, ext = os.path.splitext(imgFile.filename)
    print("get post data:%s%s"%(name,ext))
    if ext not in ('.png'):
        jsonOb['code']='error'
        jsonOb['msg']='File extension not allowed.'
        print('File extension [%s] not allowed.'%(ext))
        return json.dumps(jsonOb)
    imgFilePath = './%s%s' % (int(time.time()),ext)
    imgFile.save(imgFilePath,overwrite=True)
    
    _press_time = wechat_jump_photo.getPressTime(imgFilePath,deviceType='1920x1080',deleteImgFile=True)
    
    jsonOb['code']='ok'
    jsonOb['msg']='you need press %d.'%(_press_time)
    return json.dumps(jsonOb)
    
bottle.run(host='localhost',port=8088,debug=True)  