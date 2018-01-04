#ifndef _OS_H
#define _OS_H

typedef void (*os_proc_t)(void);
typedef void (*os_sig_t)(void);

typedef struct
{
	os_proc_t proc;
	unsigned long long period;
	int alive;
	void* data;
} task_t;

int os_task_init(task_t* task, os_proc_t proc, unsigned long long period);
int os_task_start(task_t* task);
int os_task_stop(task_t* task);

int os_signal(os_sig_t handler);
void os_exit(int value);
void* os_memcpy(void *s1, const void *s2, unsigned int n);

#endif
