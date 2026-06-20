#ifndef COMPAT_H
#define COMPAT_H

#ifdef ARDUINO

#include <Arduino.h>

#else

#include <algorithm>
#include <cctype>
#include <cstdint>
#include <cstdlib>
#include <iostream>
#include <string>

class String
{
public:
    String() = default;

    String(const char *value)
        : value_(value == nullptr ? "" : value)
    {
    }

    String(const std::string &value)
        : value_(value)
    {
    }

    String(const String &) = default;
    String &operator=(const String &) = default;

    String &operator=(const char *value)
    {
        value_ = value == nullptr ? "" : value;
        return *this;
    }

    int length() const
    {
        return static_cast<int>(value_.length());
    }

    int indexOf(const char target, int fromIndex = 0) const
    {
        if (fromIndex < 0 || fromIndex >= length())
        {
            return -1;
        }

        const std::size_t position = value_.find(target, static_cast<std::size_t>(fromIndex));
        return position == std::string::npos ? -1 : static_cast<int>(position);
    }

    int indexOf(const char *target, int fromIndex = 0) const
    {
        if (target == nullptr || fromIndex < 0 || fromIndex > length())
        {
            return -1;
        }

        const std::size_t position = value_.find(target, static_cast<std::size_t>(fromIndex));
        return position == std::string::npos ? -1 : static_cast<int>(position);
    }

    String substring(int fromIndex) const
    {
        if (fromIndex < 0 || fromIndex >= length())
        {
            return String("");
        }

        return String(value_.substr(static_cast<std::size_t>(fromIndex)));
    }

    String substring(int fromIndex, int toIndex) const
    {
        if (fromIndex < 0 || fromIndex >= length() || toIndex <= fromIndex)
        {
            return String("");
        }

        const int safeEnd = std::min(toIndex, length());
        return String(value_.substr(
            static_cast<std::size_t>(fromIndex),
            static_cast<std::size_t>(safeEnd - fromIndex)));
    }

    bool equalsIgnoreCase(const char *other) const
    {
        if (other == nullptr)
        {
            return false;
        }

        const std::string right(other);
        if (value_.length() != right.length())
        {
            return false;
        }

        for (std::size_t index = 0; index < value_.length(); ++index)
        {
            if (std::tolower(static_cast<unsigned char>(value_[index])) !=
                std::tolower(static_cast<unsigned char>(right[index])))
            {
                return false;
            }
        }

        return true;
    }

    bool startsWith(const char *prefix) const
    {
        if (prefix == nullptr)
        {
            return false;
        }

        const std::string start(prefix);
        return value_.rfind(start, 0) == 0;
    }

    void trim()
    {
        const auto first = std::find_if_not(value_.begin(), value_.end(), [](unsigned char c) {
            return std::isspace(c) != 0;
        });

        const auto last = std::find_if_not(value_.rbegin(), value_.rend(), [](unsigned char c) {
            return std::isspace(c) != 0;
        }).base();

        if (first >= last)
        {
            value_.clear();
            return;
        }

        value_ = std::string(first, last);
    }

    long toInt() const
    {
        return std::strtol(value_.c_str(), nullptr, 10);
    }

    const char *c_str() const
    {
        return value_.c_str();
    }

    std::string std() const
    {
        return value_;
    }

    String &operator+=(const char *value)
    {
        value_ += value == nullptr ? "" : value;
        return *this;
    }

    String &operator+=(const String &value)
    {
        value_ += value.value_;
        return *this;
    }

    friend bool operator==(const String &left, const char *right)
    {
        return left.value_ == (right == nullptr ? "" : right);
    }

    friend bool operator==(const String &left, const String &right)
    {
        return left.value_ == right.value_;
    }

private:
    std::string value_;
};

inline std::ostream &operator<<(std::ostream &stream, const String &value)
{
    stream << value.std();
    return stream;
}

#endif

#endif
