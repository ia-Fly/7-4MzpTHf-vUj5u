"""Fond de couverture : rend une image de la page du reel à l'instant t, sans sous-titres ni en-tête.
usage: cover_bg.py url t out.png"""
import sys, os, asyncio
from playwright.async_api import async_playwright
async def main():
    url, t, out = sys.argv[1], float(sys.argv[2]), sys.argv[3]
    async with async_playwright() as p:
        b = await p.chromium.launch(args=["--use-angle=swiftshader", "--enable-unsafe-swiftshader"])
        pg = await b.new_page(viewport={"width": 1080, "height": 1920}, device_scale_factor=1)
        root = os.environ.get("LOCAL_ROOT")
        if root:
            async def serve(route):
                rel = route.request.url.split("http://local/", 1)[1].split("?")[0]
                await route.fulfill(path=os.path.join(root, rel))
            await pg.route("http://local/**", serve)
        await pg.goto(url); await pg.wait_for_function("window.__ready === true", timeout=60000)
        await pg.evaluate(f"render({t})")
        await pg.evaluate("document.querySelectorAll('#cap,.mini,.filet2,.card,#hud2,#rewChip,#rew').forEach(e => e.style.visibility = 'hidden')")
        await pg.evaluate("new Promise(r => requestAnimationFrame(() => requestAnimationFrame(r)))")
        await pg.screenshot(path=out); await b.close()
asyncio.run(main())
