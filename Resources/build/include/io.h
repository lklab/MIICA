#ifndef _IO_H
#define _IO_H

typedef struct
{
	void* model_addr;
	int size;
	char* network_addr;
	int direction;
} io_mapping_info_t;

int io_init(void);
int io_mapping(io_mapping_info_t* mapping_list, int mapping_count);
int io_activate(unsigned long long interval);
int io_exchange(void);
int io_cleanup(void);

#endif
