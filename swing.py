import pygame
import skia
import math
import PIL.Image

WIDTH, HEIGHT = 600, 460
ANCHOR_X, ANCHOR_Y = 185, 118
ROPE_LEN = 155

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Swing")
clock = pygame.time.Clock()

surface = skia.Surface(WIDTH, HEIGHT)

CYCLE = 4.8 # seconds for one full animation cycle
RELEASE_T = 0.42 # fraction of cycle when hero lets go

frames = []
RECORD_DURATION = CYCLE  # record one full cycle
record_time = 0


LAND_T = 0.70  # fraction of cycle when hero reaches building
STAY_T = 0.90  # fraction of cycle when loop resets


def get_hero_pos(t):
    phase = (t % CYCLE) / CYCLE

    if phase < RELEASE_T:
        # swinging on the rope
        p = phase / RELEASE_T
        angle = math.radians(-52 + (52 - (-52)) * p)
        x = ANCHOR_X + ROPE_LEN * math.sin(angle)
        y = ANCHOR_Y + ROPE_LEN * math.cos(angle)
    elif phase < LAND_T:
        # flying through the air
        p = (phase - RELEASE_T) / (LAND_T - RELEASE_T)
        start_x = ANCHOR_X + ROPE_LEN * math.sin(math.radians(52))
        start_y = ANCHOR_Y + ROPE_LEN * math.cos(math.radians(52))
        end_x, end_y = 490, 160
        x = start_x + (end_x - start_x) * p
        y = start_y + (end_y - start_y) * p - 80 * math.sin(p * math.pi)
    else:
        # standing on building
        x, y = 490, 155

    return x, y

# render frames offline first
t = 0
dt = 1/60  # 60fps
total_frames = int(CYCLE * 60)

for i in range(total_frames):
    with surface as canvas:
        canvas.drawColor(skia.ColorSetRGB(135, 198, 239))
        sun_paint = skia.Paint(Color=skia.ColorSetRGB(255, 230, 100))
        canvas.drawCircle(540, 60, 35, sun_paint)
        cloud_paint = skia.Paint(Color=skia.ColorSetRGB(255, 255, 255))
        canvas.drawCircle(120, 60, 22, cloud_paint)
        canvas.drawCircle(148, 52, 28, cloud_paint)
        canvas.drawCircle(176, 60, 22, cloud_paint)
        canvas.drawCircle(340, 90, 18, cloud_paint)
        canvas.drawCircle(364, 82, 24, cloud_paint)
        canvas.drawCircle(388, 90, 18, cloud_paint)
        paint = skia.Paint(Color=skia.ColorSetRGB(138, 126, 147))
        canvas.drawRect(skia.Rect.MakeXYWH(30, 118, 160, 342), paint)
        paint.setColor(skia.ColorSetRGB(154, 141, 165))
        canvas.drawRect(skia.Rect.MakeXYWH(420, 200, 170, 260), paint)
        window_paint = skia.Paint(Color=skia.ColorSetRGB(246, 236, 200))
        for row in range(4):
            for col in range(3):
                canvas.drawRect(skia.Rect.MakeXYWH(46 + col*38, 148 + row*38, 22, 22), window_paint)
        for row in range(4):
            for col in range(3):
                canvas.drawRect(skia.Rect.MakeXYWH(438 + col*36, 220 + row*38, 22, 22), window_paint)

        hx, hy = get_hero_pos(t)
        phase = (t % CYCLE) / CYCLE

        body_paint = skia.Paint(Color=skia.ColorSetRGB(43, 58, 103))
        canvas.drawRoundRect(skia.Rect.MakeXYWH(hx-8, hy, 20, 30), 8, 8, body_paint)
        head_paint = skia.Paint(Color=skia.ColorSetRGB(192, 57, 43))
        canvas.drawCircle(hx+2, hy-10, 10, head_paint)

        arm_paint = skia.Paint(Color=skia.ColorSetRGB(192, 57, 43), StrokeWidth=6, Style=skia.Paint.kStroke_Style, StrokeCap=skia.Paint.kRound_Cap)
        canvas.drawLine(hx+12, hy+8, hx+22, hy+20, arm_paint)
        ARM_DROP_DURATION = 0.3
        if phase < RELEASE_T:
            arm_p = 0.0
        elif phase < RELEASE_T + ARM_DROP_DURATION:
            arm_p = (phase - RELEASE_T) / ARM_DROP_DURATION
        else:
            arm_p = 1.0
        arm_end_x = (hx-20) + ((hx-22) - (hx-20)) * arm_p
        arm_end_y = (hy-10) + ((hy+20) - (hy-10)) * arm_p
        canvas.drawLine(hx-8, hy+8, arm_end_x, arm_end_y, arm_paint)
        if phase < RELEASE_T:
            rope_paint = skia.Paint(Color=skia.ColorSetRGB(250, 250, 250), StrokeWidth=2, Style=skia.Paint.kStroke_Style)
            canvas.drawLine(ANCHOR_X, ANCHOR_Y, arm_end_x, arm_end_y, rope_paint)

        leg_paint = skia.Paint(Color=skia.ColorSetRGB(43, 58, 103), StrokeWidth=6, Style=skia.Paint.kStroke_Style, StrokeCap=skia.Paint.kRound_Cap)
        if phase < RELEASE_T:
            p = phase / RELEASE_T
            kick = math.sin(p * math.pi) * 20
            canvas.drawLine(hx-4, hy+30, hx-10-kick, hy+50, leg_paint)
            canvas.drawLine(hx+8, hy+30, hx+14-kick, hy+50, leg_paint)
        elif phase < RELEASE_T + 0.15:
            tuck_p = (phase - RELEASE_T) / 0.15
            tuck = tuck_p * 15
            canvas.drawLine(hx-4, hy+30, hx-10+tuck, hy+44-tuck, leg_paint)
            canvas.drawLine(hx+8, hy+30, hx+14+tuck, hy+44-tuck, leg_paint)
        else:
            straighten_p = min((phase - RELEASE_T - 0.15) / 0.15, 1.0)
            tuck = (1 - straighten_p) * 15
            canvas.drawLine(hx-4, hy+30, hx-10+tuck, hy+44-tuck, leg_paint)
            canvas.drawLine(hx+8, hy+30, hx+14+tuck, hy+44-tuck, leg_paint)

    image = surface.makeImageSnapshot()
    frames.append(PIL.Image.frombytes("RGBA", (WIDTH, HEIGHT), image.tobytes()))
    t += dt
    print(f"frame {i+1}/{total_frames}")

frames[0].save("swing.gif", save_all=True, append_images=frames[1:], loop=0, duration=1000//30)
print("saved swing.gif")
pygame.quit()