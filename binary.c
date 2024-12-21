#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <curl/curl.h>
#include <time.h>
#include <json-c/json.h>

// Telegram Bot Token
#define BOT_TOKEN "7577700170:AAGi3lcPU5Fgk5g1KAnVyr9f_xxd7QdGBOw"
#define TELEGRAM_API_URL "https://api.telegram.org/bot" BOT_TOKEN "/sendMessage"

// Admin ID
#define ADMIN_ID 6353114118

// Structure for User Access
typedef struct {
    long user_id;
    time_t expiration;
} UserAccess;

// List of users with access (basic implementation)
UserAccess user_access[100];
int user_count = 0;

// Helper function to send a message to Telegram
void send_message(long chat_id, const char *text) {
    CURL *curl;
    CURLcode res;

    char url[512];
    snprintf(url, sizeof(url), TELEGRAM_API_URL "?chat_id=%ld&text=%s", chat_id, text);

    curl = curl_easy_init();
    if (curl) {
        curl_easy_setopt(curl, CURLOPT_URL, url);
        res = curl_easy_perform(curl);
        if (res != CURLE_OK) {
            fprintf(stderr, "curl_easy_perform() failed: %s\n", curl_easy_strerror(res));
        }
        curl_easy_cleanup(curl);
    }
}

// Command: /start
void handle_start(long user_id) {
    time_t now = time(NULL);
    char response[256];

    for (int i = 0; i < user_count; i++) {
        if (user_access[i].user_id == user_id) {
            if (user_access[i].expiration > now) {
                snprintf(response, sizeof(response), "Welcome back! You have access until %s.",
                         ctime(&user_access[i].expiration));
            } else {
                snprintf(response, sizeof(response), "Your access has expired.");
            }
            send_message(user_id, response);
            return;
        }
    }

    snprintf(response, sizeof(response), "Hello! You currently don't have access. Contact an admin.");
    send_message(user_id, response);
}

// Command: /allow <user_id> <days>
void handle_allow(long admin_id, long user_id, int days) {
    if (admin_id != ADMIN_ID) {
        send_message(admin_id, "You are not authorized to use this command.");
        return;
    }

    time_t expiration = time(NULL) + (days * 24 * 3600);
    char response[256];

    for (int i = 0; i < user_count; i++) {
        if (user_access[i].user_id == user_id) {
            user_access[i].expiration = expiration;
            snprintf(response, sizeof(response), "User %ld's access updated for %d days.", user_id, days);
            send_message(admin_id, response);
            return;
        }
    }

    user_access[user_count].user_id = user_id;
    user_access[user_count].expiration = expiration;
    user_count++;

    snprintf(response, sizeof(response), "User %ld has been granted access for %d days.", user_id, days);
    send_message(admin_id, response);
}

// Main function
int main() {
    // Simulate Telegram command handling
    handle_start(12345);          // User without access
    handle_allow(ADMIN_ID, 12345, 7); // Admin grants access
    handle_start(12345);          // User with access

    return 0;
}
