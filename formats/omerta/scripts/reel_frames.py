import sys, os, asyncio, subprocess
from playwright.async_api import async_playwright
# usage: reel_frames.py url mode out [times...]
#   mode=preview : out = prefix, times listed -> prefix_<t>.png
#   mode=video   : out = path of raw video (mp4, no audio), renders fps*dur frames
async def main():
    url, mode, out = sys.argv[1], sys.argv[2], sys.argv[3]
    async with async_playwright() as p:
        b = await p.chromium.launch(args=["--use-angle=swiftshader", "--enable-unsafe-swiftshader"])
        pg = await b.new_page(viewport={"width": 1080, "height": 1920}, device_scale_factor=1)
        errs = []
        pg.on("pageerror", lambda e: errs.append(str(e)))
        root = os.environ.get("LOCAL_ROOT")
        if root:  # sert les fichiers locaux sans serveur HTTP : http://local/<chemin> -> root/<chemin>
            async def serve(route):
                rel = route.request.url.split("http://local/", 1)[1].split("?")[0]
                await route.fulfill(path=os.path.join(root, rel))
            await pg.route("http://local/**", serve)
        await pg.goto(url)
        await pg.wait_for_function("window.__ready === true", timeout=60000)
        if mode == "preview":
            for ts in sys.argv[4:]:
                await pg.evaluate(f"render({float(ts)})")
                await pg.evaluate("new Promise(r => requestAnimationFrame(() => requestAnimationFrame(r)))")
                await pg.screenshot(path=f"{out}_{ts}.png")
        else:
            fps, dur = 30, float(sys.argv[4])
            n = int(round(fps * dur)); i0 = int(round(fps * float(sys.argv[5]))) if len(sys.argv) > 5 else 0
            ff = subprocess.Popen(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-f", "image2pipe", "-framerate", str(fps), "-i", "-",
                                   "-c:v", "libx264", "-preset", "medium", "-crf", "12", "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)
            for i in range(i0, n):
                await pg.evaluate(f"render({i / fps})")
                await pg.evaluate("new Promise(r => requestAnimationFrame(() => requestAnimationFrame(r)))")
                ff.stdin.write(await pg.screenshot(type="png"))
                if i % 60 == 0: print("frame", i, flush=True)
            ff.stdin.close(); ff.wait()
        print("errors:", errs[:5])
        await b.close()
asyncio.run(main())
