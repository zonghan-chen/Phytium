CC = gcc

main: main.c china.o phytium.o
	$(CC) -o main main.c china.o phytium.o

china.o: china.c
	$(CC) -c china.c

phytium.o: phytium.c
	$(CC) -c phytium.c

clean:
	rm -f *.o main main.exe
