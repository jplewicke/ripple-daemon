LIMIT=$RANDOM
PERCENT=0.1
head -60 nodes | awk '{print "node 1.0 " $1}' > tmp
awk '{print "person " $1}' people >> tmp
for ((a=1; a <= LIMIT ; a++))
do
  echo "$a $RANDOM $RANDOM $RANDOM $RANDOM bid" >> tmp
done

awk '$1 ~ /node/ {v[NR] = $2; n[NR] = $3 ; last = NR} $1 ~ /person/ { p[NR - last] = $2; lastp = NR - last} $6 ~ /bid/ && ($2 % last != $3 % last) {printf("bid_%d|%s,%s,%s,%0.f,%f,\n", $1,p[$1 % lastp + 1], n[$2 % last + 1], n[$3 % last + 1], $4 % 100 + 1, (v[$3 % last + 1] / v[$2 % last + 1]) / (0.99 + rand() * '$PERCENT')) }' tmp