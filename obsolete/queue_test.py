"""
make a list
pop all elements except the first one and put them into a new list
shuffle the list
put back the shuffled elements on the old list
"""

""" import random

list = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
temp_list = list[1:]

print(list)
for item in range(1, len(list)):
    list.pop()
print(list)
random.shuffle(temp_list)
list += temp_list
print(list) """

""" my_list = [1, 2, 3, 4, 5, 6, 7, 8, 9]

# How many elements each list should have
n = 4

# using list comprehension
final = [my_list[i * n:(i + 1) * n] for i in range((len(my_list) + n - 1) // n )]
print (final) """

l = [1, 2, 3, 4, 5, 6, 7, 8, 9]

n = 4

x = [l[i:i + n] for i in range(0, len(l), n)]
print(x)

song_queue_temp = self.song_queue
            song_queue_chunk_size = 10
            # song_queue_chunked = [song_queue_temp[i * song_queue_chunk_size:(i + 1) * song_queue_chunk_size] for i in range((len(song_queue_temp) + song_queue_chunk_size - 1) // song_queue_chunk_size )]