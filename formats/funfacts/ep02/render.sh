cd /home/claude/fact2
export LOCAL_ROOT=/home/claude/fact2/planches
python3 rf2.py http://local/reel.html video out/part1.mp4 28.0 0 420 > out/r1.log 2>&1 &
python3 rf2.py http://local/reel.html video out/part2.mp4 28.0 14.0 840 > out/r2.log 2>&1 &
wait
echo done > out/render.done
