import heapq

gen1 = (x for x in range(1, 10, 2))
gen2 = (y for y in range(2, 21, 2))


gen = heapq.merge(gen1, gen2)
print(list(gen))
