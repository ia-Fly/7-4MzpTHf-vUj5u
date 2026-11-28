cd /home/claude/ff5
export LOCAL_ROOT=/home/claude/ff5/planches
python3 rf2.py http://local/reel.html video out/part1.mp4 28.5 0 428 > out/r1.log 2>&1 &
python3 rf2.py http://local/reel.html video out/part2.mp4 28.5 14.2667 855 > out/r2.log 2>&1 &
wait
echo done > out/render.done
