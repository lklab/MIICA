#ifndef _IO_H
#define _IO_H

int io_init(void);
int io_mapping(void* variable, int size, char* address, int direction);
int io_exchange(void);
int io_cleanup(void);

#endif
