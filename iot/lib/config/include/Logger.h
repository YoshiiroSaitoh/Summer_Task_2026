#ifndef LOGGER_H
#define LOGGER_H

#include <Compat.h>

#ifdef ARDUINO
#include <Arduino.h>
#else
#include <cstdio>
#endif

namespace Logger
{
enum class Level
{
    Debug,
    Info,
    Warning,
    Error
};

inline const char *levelName(Level level)
{
    switch (level)
    {
    case Level::Debug:
        return "DEBUG";
    case Level::Info:
        return "INFO";
    case Level::Warning:
        return "WARN";
    case Level::Error:
        return "ERROR";
    default:
        return "INFO";
    }
}

inline void begin(unsigned long baud = 115200)
{
#ifdef ARDUINO
    Serial.begin(baud);
#else
    (void)baud;
#endif
}

inline void writeLine(Level level, const char *message)
{
#ifdef ARDUINO
    Serial.print("[");
    Serial.print(levelName(level));
    Serial.print("] ");
    Serial.println(message);
#else
    std::printf("[%s] %s\n", levelName(level), message);
#endif
}

inline void writeLine(Level level, const String &message)
{
    writeLine(level, message.c_str());
}

template <typename... Args>
inline void debugf(const char *format, Args... args)
{
    char buffer[256];
    std::snprintf(buffer, sizeof(buffer), format, args...);
    writeLine(Level::Debug, buffer);
}

template <typename... Args>
inline void infof(const char *format, Args... args)
{
    char buffer[256];
    std::snprintf(buffer, sizeof(buffer), format, args...);
    writeLine(Level::Info, buffer);
}

template <typename... Args>
inline void warnf(const char *format, Args... args)
{
    char buffer[256];
    std::snprintf(buffer, sizeof(buffer), format, args...);
    writeLine(Level::Warning, buffer);
}

template <typename... Args>
inline void errorf(const char *format, Args... args)
{
    char buffer[256];
    std::snprintf(buffer, sizeof(buffer), format, args...);
    writeLine(Level::Error, buffer);
}

inline void info(const String &message)
{
    writeLine(Level::Info, message);
}

inline void debug(const String &message)
{
    writeLine(Level::Debug, message);
}

inline void warn(const String &message)
{
    writeLine(Level::Warning, message);
}

inline void error(const String &message)
{
    writeLine(Level::Error, message);
}
}

#endif
