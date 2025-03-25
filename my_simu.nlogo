extensions [array vid]
globals [
  width ;定义交叉口宽度
  time
  traj-data   ;轨迹数据
  left-arc ; 左转弧度
  right-arc ;右转弧度
]

turtles-own [
  id
  v
  arr-x
  arr-y
  arr-v
  lane-label
]

to setup
  clear-all
  set time 0
  set left-arc 6.25 * pi / 2
  set right-arc 0.75 * pi / 2
  ;set-patch-size 7
  ;resize-world -90 90 -90 90
  draw-road
  init-cars
  reset-ticks
  if vid:recorder-status = "recording" [repeat 1[vid:record-view ]]
end

to go
  if ticks >= 95 [vid:stop stop]
  ask turtles [move-cars]
  ask turtles with [xcor >= world-width] [die]
  ask turtles [show-car-id]
  set time time + 1
  tick


  if vid:recorder-status = "recording" [ repeat 1[vid:record-view ]]
end

to draw-road
  ask patches [set pcolor green] ;设置绿地颜色
  set width 10 ;交叉口宽度为10个瓦片, 每个瓦片代表2.5米
  ask patches with [abs pycor <= (width / 2) or abs pxcor <= (width / 2)] [
    set pcolor grey - 2.5 + random-float 0.25
  ]
  draw-all-lines
end

to draw-all-lines
  ;画黄色线
  foreach [-0.5 0.5 -5 5] [ p ->
    foreach [90 0] [ head ->
      draw-yellow-line head p
    ]
  ]
  ;画白色线
  foreach [-2 2 -3.5 3.5] [ p ->
    foreach [90 0] [ head ->
      draw-white-line head p
    ]
  ]
end

to draw-yellow-line [head p]
  create-turtles 1 [
    ifelse head = 90
    [setxy min-pxcor p]
    [setxy p min-pycor]
    hide-turtle
    set color yellow
    set heading head
    pen-down
    ;set pen-size 2
    fd (world-width / 2 - width / 2) - 0.5
    pen-up
    fd width + 0.5
    pen-down
    fd (world-width / 2 - width / 2)
    die
  ]
end

to draw-white-line [head p]

  create-turtles 1 [
    ifelse head = 90
    [setxy min-pxcor p]
    [setxy p min-pycor]
    hide-turtle
    set color white
    set heading head
    ;set pen-size 2
    repeat (world-width / 2 - width / 2) / 2 + 1[
      pen-down
      fd 1
      pen-up
      fd 1
    ]
    fd width - 0.5
    repeat (world-width / 2 - width / 2) / 2 + 1[
      pen-down
      fd 1
      pen-up
      fd 1
    ]
    die
  ]
end

to init-cars
  ;到时候这部分可以从文件中读取数据，不用这么麻烦一个个写
  let file-path "D://Luke//Desktop//智能网联车在无信号交叉口的轨迹计算研究//代码//model1.txt"
  ifelse (file-exists? file-path)[
    set traj-data []
    file-open file-path
    while [not file-at-end?] [
      ;let line-data file-read-line
      let row (list file-read file-read file-read file-read file-read file-read)
      ;let row (map [value -> read-from-string value] values)
      set traj-data lput row traj-data
    ]
    ;print length traj-data
    file-close
  ] [
    user-message "There is no results.txt file in current directory!"
  ]
  ;已读取所有数据，开始遍历生成
  ifelse (is-list? traj-data)[
    let x-list []
    let y-list []
    let v-list []
    let lane 11
    let local-id 1
    foreach traj-data [ six-tuple ->
      ;是同一个车的轨迹
      ifelse (item 0 six-tuple = lane) and (item 1 six-tuple = local-id) [
        set x-list sentence x-list (item 3 six-tuple)
        set y-list sentence y-list (item 4 six-tuple)
        set v-list sentence v-list (item 5 six-tuple)
      ][
        ;不是同一个车的轨迹了，所以先创建上一个车的turtle
        create-car x-list y-list v-list lane local-id
        ;先清空所有轨迹数据
        set x-list []
        set y-list []
        set v-list []
        ;将每辆车的第一时刻轨迹存储起来
        set x-list sentence x-list (item 3 six-tuple)
        set y-list sentence y-list (item 4 six-tuple)
        set v-list sentence v-list (item 5 six-tuple)
      ]
      set lane (item 0 six-tuple)
      set local-id (item 1 six-tuple)
    ]
    ;遍历完后，还需要生成最后一辆车
    create-car x-list y-list v-list lane local-id
    ;print lane
    ;print local-id
    ;print count turtles
  ] [user-message "You need to load in trajectory data first!"]

end

to create-car [x-list y-list v-list lane local-id]
  ;print lane
  ;print local-id
  ;print length x-list
  ;print length y-list
  create-turtles 1 [
          set arr-x array:from-list x-list
          set arr-y array:from-list y-list
          set arr-v array:from-list v-list
          set lane-label lane
          set id local-id
          setxy ((array:item arr-x 0) / 2.5  - width / 2 ) ((array:item arr-y 0) / 2.5  - width / 2 )
          set v (array:item arr-v 0)
          set shape "car top"
          set size 2
          if lane = 11 [set color 15 set heading 0 set label-color 65]
          if lane = 12 [set color 25 set heading 0 set label-color 75]
          if lane = 13 [set color 35 set heading 0 set label-color 85]
          if lane = 21 [set color 45 set heading 270 set label-color 95]
          if lane = 22 [set color 55 set heading 270 set label-color 105]
          if lane = 23 [set color 65 set heading 270 set label-color 115]
          if lane = 31 [set color 75 set heading 180 set label-color 125]
          if lane = 32 [set color 85 set heading 180 set label-color 15]
          if lane = 33 [set color 95 set heading 180 set label-color 25]
          if lane = 41 [set color 105 set heading 90 set label-color 35]
          if lane = 42 [set color 115 set heading 90 set label-color 45]
          if lane = 43 [set color 125 set heading 90 set label-color 55]
          show-car-id
   ]
end

to show-car-id
  ifelse show-id?[
    set label id
  ][set label ""]
end

to move-cars
  ;if time > array:length arr-x [stop]
  let x-next (array:item arr-x time) / 2.5  - width / 2
  let y-next (array:item arr-y time) / 2.5  - width / 2
  ifelse (x-next < min-pxcor) or (x-next > max-pxcor) or (y-next < min-pycor) or (y-next > max-pycor) [
    die
  ][
    let x-temp xcor ;将前一时刻的位置信息存储起来用于改变车辆朝向角度
    let y-temp ycor ;将前一时刻的位置信息存储起来用于改变车辆朝向角度
    setxy x-next y-next ;更新现在的位置
    set v (array:item arr-v time)
    let is-cz (xcor > width / -2 and xcor < width / 2) and (ycor > width / -2 and ycor < width / 2) ;判断是不是在交叉口内
    let turn-left member? lane-label [11 21 33 43]  ;判断是不是左转
    let turn-right member? lane-label [13 23 31 41] ;判断是不是右转
    if is-cz and turn-left [ lt sqrt((x-temp - xcor) * (x-temp - xcor) + (y-temp - ycor) * (y-temp - ycor)) / left-arc * 90] ;左转半径更大
    if is-cz and turn-right [ rt sqrt((x-temp - xcor) * (x-temp - xcor) + (y-temp - ycor) * (y-temp - ycor)) / right-arc * 90] ;右转半径更小
    set-heading ;设置通过交叉口后的朝向
  ]
end

to set-heading
  ;下面是通过交叉口后，左转和右转车辆朝向的改变
  if lane-label = 11 and xcor < width / -2 [ set heading 270]
  if lane-label = 21 and ycor < width / -2 [ set heading 180]
  if lane-label = 33 and xcor > width / 2 [ set heading 90]
  if lane-label = 43 and ycor > width / 2 [ set heading 0]
  if lane-label = 13 and xcor > width / 2 [ set heading 90]
  if lane-label = 23 and ycor > width / 2 [ set heading 0]
  if lane-label = 31 and xcor < width / -2 [ set heading 270]
  if lane-label = 41 and ycor < width / -2 [ set heading 180]
end

to start-recorder
  carefully [
    vid:start-recorder
  ] [ user-message error-message ]
end

to reset-recorder
  let message (word
    "If you reset the recorder, the current recording will be lost."
    "Are you sure you want to reset the recorder?")
  if vid:recorder-status = "inactive" or user-yes-or-no? message [
    vid:reset-recorder
  ]
end

to save-recording
  if vid:recorder-status = "inactive" [
    user-message "The recorder is inactive. There is nothing to save."
    stop
  ]
  ; prompt user for movie location
  ;user-message (word "Choose a name for your movie file (the .mp4 extension will be automatically added).")
  ;let path user-new-file
  let path "D:\\Luke\\Desktop\\智能网联车在无信号交叉口的轨迹计算研究\\代码\\out\\model1.mp4"
  ;if not is-string? path [ stop ]  ; stop if user canceled
  ; export the movie
  carefully [
    vid:save-recording path
    user-message (word "Exported movie to " path ".")
  ] [
    user-message error-message
  ]
end
@#$#@#$#@
GRAPHICS-WINDOW
247
113
1522
1389
-1
-1
7.0
1
10
1
1
1
0
0
0
1
-90
90
-90
90
0
0
1
ticks
2.0

BUTTON
18
450
84
483
NIL
setup\n
NIL
1
T
OBSERVER
NIL
NIL
NIL
NIL
1

BUTTON
96
450
159
483
NIL
go
T
1
T
OBSERVER
NIL
NIL
NIL
NIL
1

BUTTON
21
564
156
597
start recorder
start-recorder
NIL
1
T
OBSERVER
NIL
NIL
NIL
NIL
1

BUTTON
20
604
156
637
reset recorder
reset-recorder
NIL
1
T
OBSERVER
NIL
NIL
NIL
NIL
1

BUTTON
22
705
158
740
save recording
save-recording
NIL
1
T
OBSERVER
NIL
NIL
NIL
NIL
1

MONITOR
18
652
162
697
NIL
vid:recorder-status
17
1
11

SWITCH
22
517
157
550
show-id?
show-id?
0
1
-1000

PLOT
0
1403
1005
2017
平均速度变化图
time
v
0.0
95.0
0.0
17.0
true
false
"" ""
PENS
"default" 1.0 0 -2674135 true "" "plot mean [v] of turtles"

@#$#@#$#@
## WHAT IS IT?

(a general understanding of what the model is trying to show or explain)

## HOW IT WORKS

(what rules the agents use to create the overall behavior of the model)

## HOW TO USE IT

(how to use the model, including a description of each of the items in the Interface tab)

## THINGS TO NOTICE

(suggested things for the user to notice while running the model)

## THINGS TO TRY

(suggested things for the user to try to do (move sliders, switches, etc.) with the model)

## EXTENDING THE MODEL

(suggested things to add or change in the Code tab to make the model more complicated, detailed, accurate, etc.)

## NETLOGO FEATURES

(interesting or unusual features of NetLogo that the model uses, particularly in the Code tab; or where workarounds were needed for missing features)

## RELATED MODELS

(models in the NetLogo Models Library and elsewhere which are of related interest)

## CREDITS AND REFERENCES

(a reference to the model's URL on the web if it has one, as well as any other necessary credits, citations, and links)
@#$#@#$#@
default
true
0
Polygon -7500403 true true 150 5 40 250 150 205 260 250

airplane
true
0
Polygon -7500403 true true 150 0 135 15 120 60 120 105 15 165 15 195 120 180 135 240 105 270 120 285 150 270 180 285 210 270 165 240 180 180 285 195 285 165 180 105 180 60 165 15

arrow
true
0
Polygon -7500403 true true 150 0 0 150 105 150 105 293 195 293 195 150 300 150

box
false
0
Polygon -7500403 true true 150 285 285 225 285 75 150 135
Polygon -7500403 true true 150 135 15 75 150 15 285 75
Polygon -7500403 true true 15 75 15 225 150 285 150 135
Line -16777216 false 150 285 150 135
Line -16777216 false 150 135 15 75
Line -16777216 false 150 135 285 75

bug
true
0
Circle -7500403 true true 96 182 108
Circle -7500403 true true 110 127 80
Circle -7500403 true true 110 75 80
Line -7500403 true 150 100 80 30
Line -7500403 true 150 100 220 30

butterfly
true
0
Polygon -7500403 true true 150 165 209 199 225 225 225 255 195 270 165 255 150 240
Polygon -7500403 true true 150 165 89 198 75 225 75 255 105 270 135 255 150 240
Polygon -7500403 true true 139 148 100 105 55 90 25 90 10 105 10 135 25 180 40 195 85 194 139 163
Polygon -7500403 true true 162 150 200 105 245 90 275 90 290 105 290 135 275 180 260 195 215 195 162 165
Polygon -16777216 true false 150 255 135 225 120 150 135 120 150 105 165 120 180 150 165 225
Circle -16777216 true false 135 90 30
Line -16777216 false 150 105 195 60
Line -16777216 false 150 105 105 60

car
false
0
Polygon -7500403 true true 300 180 279 164 261 144 240 135 226 132 213 106 203 84 185 63 159 50 135 50 75 60 0 150 0 165 0 225 300 225 300 180
Circle -16777216 true false 180 180 90
Circle -16777216 true false 30 180 90
Polygon -16777216 true false 162 80 132 78 134 135 209 135 194 105 189 96 180 89
Circle -7500403 true true 47 195 58
Circle -7500403 true true 195 195 58

car top
true
0
Polygon -7500403 true true 151 8 119 10 98 25 86 48 82 225 90 270 105 289 150 294 195 291 210 270 219 225 214 47 201 24 181 11
Polygon -16777216 true false 210 195 195 210 195 135 210 105
Polygon -16777216 true false 105 255 120 270 180 270 195 255 195 225 105 225
Polygon -16777216 true false 90 195 105 210 105 135 90 105
Polygon -1 true false 205 29 180 30 181 11
Line -7500403 false 210 165 195 165
Line -7500403 false 90 165 105 165
Polygon -16777216 true false 121 135 180 134 204 97 182 89 153 85 120 89 98 97
Line -16777216 false 210 90 195 30
Line -16777216 false 90 90 105 30
Polygon -1 true false 95 29 120 30 119 11

circle
false
0
Circle -7500403 true true 0 0 300

circle 2
false
0
Circle -7500403 true true 0 0 300
Circle -16777216 true false 30 30 240

cow
false
0
Polygon -7500403 true true 200 193 197 249 179 249 177 196 166 187 140 189 93 191 78 179 72 211 49 209 48 181 37 149 25 120 25 89 45 72 103 84 179 75 198 76 252 64 272 81 293 103 285 121 255 121 242 118 224 167
Polygon -7500403 true true 73 210 86 251 62 249 48 208
Polygon -7500403 true true 25 114 16 195 9 204 23 213 25 200 39 123

cylinder
false
0
Circle -7500403 true true 0 0 300

dot
false
0
Circle -7500403 true true 90 90 120

face happy
false
0
Circle -7500403 true true 8 8 285
Circle -16777216 true false 60 75 60
Circle -16777216 true false 180 75 60
Polygon -16777216 true false 150 255 90 239 62 213 47 191 67 179 90 203 109 218 150 225 192 218 210 203 227 181 251 194 236 217 212 240

face neutral
false
0
Circle -7500403 true true 8 7 285
Circle -16777216 true false 60 75 60
Circle -16777216 true false 180 75 60
Rectangle -16777216 true false 60 195 240 225

face sad
false
0
Circle -7500403 true true 8 8 285
Circle -16777216 true false 60 75 60
Circle -16777216 true false 180 75 60
Polygon -16777216 true false 150 168 90 184 62 210 47 232 67 244 90 220 109 205 150 198 192 205 210 220 227 242 251 229 236 206 212 183

fish
false
0
Polygon -1 true false 44 131 21 87 15 86 0 120 15 150 0 180 13 214 20 212 45 166
Polygon -1 true false 135 195 119 235 95 218 76 210 46 204 60 165
Polygon -1 true false 75 45 83 77 71 103 86 114 166 78 135 60
Polygon -7500403 true true 30 136 151 77 226 81 280 119 292 146 292 160 287 170 270 195 195 210 151 212 30 166
Circle -16777216 true false 215 106 30

flag
false
0
Rectangle -7500403 true true 60 15 75 300
Polygon -7500403 true true 90 150 270 90 90 30
Line -7500403 true 75 135 90 135
Line -7500403 true 75 45 90 45

flower
false
0
Polygon -10899396 true false 135 120 165 165 180 210 180 240 150 300 165 300 195 240 195 195 165 135
Circle -7500403 true true 85 132 38
Circle -7500403 true true 130 147 38
Circle -7500403 true true 192 85 38
Circle -7500403 true true 85 40 38
Circle -7500403 true true 177 40 38
Circle -7500403 true true 177 132 38
Circle -7500403 true true 70 85 38
Circle -7500403 true true 130 25 38
Circle -7500403 true true 96 51 108
Circle -16777216 true false 113 68 74
Polygon -10899396 true false 189 233 219 188 249 173 279 188 234 218
Polygon -10899396 true false 180 255 150 210 105 210 75 240 135 240

house
false
0
Rectangle -7500403 true true 45 120 255 285
Rectangle -16777216 true false 120 210 180 285
Polygon -7500403 true true 15 120 150 15 285 120
Line -16777216 false 30 120 270 120

leaf
false
0
Polygon -7500403 true true 150 210 135 195 120 210 60 210 30 195 60 180 60 165 15 135 30 120 15 105 40 104 45 90 60 90 90 105 105 120 120 120 105 60 120 60 135 30 150 15 165 30 180 60 195 60 180 120 195 120 210 105 240 90 255 90 263 104 285 105 270 120 285 135 240 165 240 180 270 195 240 210 180 210 165 195
Polygon -7500403 true true 135 195 135 240 120 255 105 255 105 285 135 285 165 240 165 195

line
true
0
Line -7500403 true 150 0 150 300

line half
true
0
Line -7500403 true 150 0 150 150

pentagon
false
0
Polygon -7500403 true true 150 15 15 120 60 285 240 285 285 120

person
false
0
Circle -7500403 true true 110 5 80
Polygon -7500403 true true 105 90 120 195 90 285 105 300 135 300 150 225 165 300 195 300 210 285 180 195 195 90
Rectangle -7500403 true true 127 79 172 94
Polygon -7500403 true true 195 90 240 150 225 180 165 105
Polygon -7500403 true true 105 90 60 150 75 180 135 105

plant
false
0
Rectangle -7500403 true true 135 90 165 300
Polygon -7500403 true true 135 255 90 210 45 195 75 255 135 285
Polygon -7500403 true true 165 255 210 210 255 195 225 255 165 285
Polygon -7500403 true true 135 180 90 135 45 120 75 180 135 210
Polygon -7500403 true true 165 180 165 210 225 180 255 120 210 135
Polygon -7500403 true true 135 105 90 60 45 45 75 105 135 135
Polygon -7500403 true true 165 105 165 135 225 105 255 45 210 60
Polygon -7500403 true true 135 90 120 45 150 15 180 45 165 90

sheep
false
15
Circle -1 true true 203 65 88
Circle -1 true true 70 65 162
Circle -1 true true 150 105 120
Polygon -7500403 true false 218 120 240 165 255 165 278 120
Circle -7500403 true false 214 72 67
Rectangle -1 true true 164 223 179 298
Polygon -1 true true 45 285 30 285 30 240 15 195 45 210
Circle -1 true true 3 83 150
Rectangle -1 true true 65 221 80 296
Polygon -1 true true 195 285 210 285 210 240 240 210 195 210
Polygon -7500403 true false 276 85 285 105 302 99 294 83
Polygon -7500403 true false 219 85 210 105 193 99 201 83

square
false
0
Rectangle -7500403 true true 30 30 270 270

square 2
false
0
Rectangle -7500403 true true 30 30 270 270
Rectangle -16777216 true false 60 60 240 240

star
false
0
Polygon -7500403 true true 151 1 185 108 298 108 207 175 242 282 151 216 59 282 94 175 3 108 116 108

target
false
0
Circle -7500403 true true 0 0 300
Circle -16777216 true false 30 30 240
Circle -7500403 true true 60 60 180
Circle -16777216 true false 90 90 120
Circle -7500403 true true 120 120 60

tree
false
0
Circle -7500403 true true 118 3 94
Rectangle -6459832 true false 120 195 180 300
Circle -7500403 true true 65 21 108
Circle -7500403 true true 116 41 127
Circle -7500403 true true 45 90 120
Circle -7500403 true true 104 74 152

triangle
false
0
Polygon -7500403 true true 150 30 15 255 285 255

triangle 2
false
0
Polygon -7500403 true true 150 30 15 255 285 255
Polygon -16777216 true false 151 99 225 223 75 224

truck
false
0
Rectangle -7500403 true true 4 45 195 187
Polygon -7500403 true true 296 193 296 150 259 134 244 104 208 104 207 194
Rectangle -1 true false 195 60 195 105
Polygon -16777216 true false 238 112 252 141 219 141 218 112
Circle -16777216 true false 234 174 42
Rectangle -7500403 true true 181 185 214 194
Circle -16777216 true false 144 174 42
Circle -16777216 true false 24 174 42
Circle -7500403 false true 24 174 42
Circle -7500403 false true 144 174 42
Circle -7500403 false true 234 174 42

turtle
true
0
Polygon -10899396 true false 215 204 240 233 246 254 228 266 215 252 193 210
Polygon -10899396 true false 195 90 225 75 245 75 260 89 269 108 261 124 240 105 225 105 210 105
Polygon -10899396 true false 105 90 75 75 55 75 40 89 31 108 39 124 60 105 75 105 90 105
Polygon -10899396 true false 132 85 134 64 107 51 108 17 150 2 192 18 192 52 169 65 172 87
Polygon -10899396 true false 85 204 60 233 54 254 72 266 85 252 107 210
Polygon -7500403 true true 119 75 179 75 209 101 224 135 220 225 175 261 128 261 81 224 74 135 88 99

wheel
false
0
Circle -7500403 true true 3 3 294
Circle -16777216 true false 30 30 240
Line -7500403 true 150 285 150 15
Line -7500403 true 15 150 285 150
Circle -7500403 true true 120 120 60
Line -7500403 true 216 40 79 269
Line -7500403 true 40 84 269 221
Line -7500403 true 40 216 269 79
Line -7500403 true 84 40 221 269

wolf
false
0
Polygon -16777216 true false 253 133 245 131 245 133
Polygon -7500403 true true 2 194 13 197 30 191 38 193 38 205 20 226 20 257 27 265 38 266 40 260 31 253 31 230 60 206 68 198 75 209 66 228 65 243 82 261 84 268 100 267 103 261 77 239 79 231 100 207 98 196 119 201 143 202 160 195 166 210 172 213 173 238 167 251 160 248 154 265 169 264 178 247 186 240 198 260 200 271 217 271 219 262 207 258 195 230 192 198 210 184 227 164 242 144 259 145 284 151 277 141 293 140 299 134 297 127 273 119 270 105
Polygon -7500403 true true -1 195 14 180 36 166 40 153 53 140 82 131 134 133 159 126 188 115 227 108 236 102 238 98 268 86 269 92 281 87 269 103 269 113

x
false
0
Polygon -7500403 true true 270 75 225 30 30 225 75 270
Polygon -7500403 true true 30 75 75 30 270 225 225 270
@#$#@#$#@
NetLogo 6.3.0
@#$#@#$#@
@#$#@#$#@
@#$#@#$#@
@#$#@#$#@
@#$#@#$#@
default
0.0
-0.2 0 0.0 1.0
0.0 1 1.0 0.0
0.2 0 0.0 1.0
link direction
true
0
Line -7500403 true 150 150 90 180
Line -7500403 true 150 150 210 180
@#$#@#$#@
0
@#$#@#$#@
