import tasko


async def blink(led=None, interval=0.5, times=3, color=(0, 255, 0)):
    if not led:
        return

    for i in range(0, times):
        led.fill(color)
        await tasko.sleep(interval)
        led.fill(0)
        await tasko.sleep(interval)
