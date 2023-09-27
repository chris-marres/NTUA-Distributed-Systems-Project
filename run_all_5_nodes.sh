for file in $(ls compose/)
    do docker compose -f compose/$file up
done