cd /home/claude/fact1
export LOCAL_ROOT=/home/claude/fact1/planches
python3 rf2.py http://local/reel.html video out/part1.mp4 28.9 0 434 > out/r1.log 2>&1 &
python3 rf2.py http://local/reel.html video out/part2.mp4 28.9 14.4666667 867 > out/r2.log 2>&1 &
wait
echo done > out/render.done
