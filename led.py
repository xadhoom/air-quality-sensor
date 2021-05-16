import tasko


async def blink(led, interval=0.5, times=3, color=(0, 255, 0)):
    print("In blink led")
    for i in range(1, times):
        led.fill(color)
        await tasko.sleep(interval)
        led.fill(0)
        await tasko.sleep(interval)
