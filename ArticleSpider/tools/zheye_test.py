# coding:utf-8
from tools.zheye import zheye
z = zheye()
positions = z.Recognize('zhihu_image/e.gif')
last_position = []
if len(positions) == 2:
    if positions[0][1] > positions[1][1]:
        last_position.append([positions[1][1], positions[1][0]])
        last_position.append([positions[0][1], positions[0][0]])
    else:
        last_position.append([positions[0][1], positions[0][0]])
        last_position.append([positions[1][1], positions[1][0]])
else:
    last_position.append([positions[0][1], positions[0][0]])

print(last_position)