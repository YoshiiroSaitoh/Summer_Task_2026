#include "DS18B20Provider.h"

#ifdef ARDUINO
#include <Arduino.h>
#include <Logger.h>
#include <cstdio>

namespace
{
constexpr unsigned long ConversionDelayMs = 750;
constexpr uint8_t ReadRomCommand = 0x33;
constexpr uint8_t SkipRomCommand = 0xCC;
constexpr uint8_t ConvertTCommand = 0x44;
constexpr uint8_t ReadScratchpadCommand = 0xBE;

uint8_t crc8(const uint8_t *data, int length)
{
    uint8_t crc = 0;
    for (int index = 0; index < length; ++index)
    {
        uint8_t value = data[index];
        for (int bit = 0; bit < 8; ++bit)
        {
            const uint8_t mix = (crc ^ value) & 0x01;
            crc >>= 1;
            if (mix != 0)
            {
                crc ^= 0x8C;
            }
            value >>= 1;
        }
    }

    return crc;
}

String formatRomId(const uint8_t rom[8])
{
    char buffer[3];
    String formatted;

    for (int index = 0; index < 8; ++index)
    {
        if (index == 1)
        {
            formatted += "-";
        }

        std::snprintf(buffer, sizeof(buffer), "%02X", rom[index]);
        formatted += buffer;
    }

    return formatted;
}
}

DS18B20Provider::DS18B20Provider(uint8_t pin)
    : pin_(pin), probeId_(), probeIdInitialized_(false)
{
}

bool resetOneWireBus(uint8_t pin)
{
    pinMode(pin, OUTPUT);
    digitalWrite(pin, LOW);
    delayMicroseconds(480);

    pinMode(pin, INPUT_PULLUP);
    delayMicroseconds(70);

    const bool presenceDetected = digitalRead(pin) == LOW;
    delayMicroseconds(410);
    return presenceDetected;
}

void writeOneWireBit(uint8_t pin, bool value)
{
    pinMode(pin, OUTPUT);
    digitalWrite(pin, LOW);

    if (value)
    {
        delayMicroseconds(6);
        pinMode(pin, INPUT_PULLUP);
        delayMicroseconds(64);
        return;
    }

    delayMicroseconds(60);
    pinMode(pin, INPUT_PULLUP);
    delayMicroseconds(10);
}

bool readOneWireBit(uint8_t pin)
{
    pinMode(pin, OUTPUT);
    digitalWrite(pin, LOW);
    delayMicroseconds(6);

    pinMode(pin, INPUT_PULLUP);
    delayMicroseconds(9);

    const bool bitValue = digitalRead(pin) == HIGH;
    delayMicroseconds(55);
    return bitValue;
}

void writeOneWireByte(uint8_t pin, uint8_t value)
{
    for (int bit = 0; bit < 8; ++bit)
    {
        writeOneWireBit(pin, (value & 0x01) != 0);
        value >>= 1;
    }
}

uint8_t readOneWireByte(uint8_t pin)
{
    uint8_t value = 0;
    for (int bit = 0; bit < 8; ++bit)
    {
        if (readOneWireBit(pin))
        {
            value |= static_cast<uint8_t>(1U << bit);
        }
    }

    return value;
}

bool readOneWireBytes(uint8_t pin, uint8_t *buffer, int length)
{
    if (buffer == nullptr || length <= 0)
    {
        return false;
    }

    for (int index = 0; index < length; ++index)
    {
        buffer[index] = readOneWireByte(pin);
    }

    return true;
}

bool readProbeId(uint8_t pin, String &probeId)
{
    if (!resetOneWireBus(pin))
    {
        return false;
    }

    writeOneWireByte(pin, ReadRomCommand);

    uint8_t rom[8];
    if (!readOneWireBytes(pin, rom, 8))
    {
        return false;
    }

    if (crc8(rom, 7) != rom[7])
    {
        return false;
    }

    probeId = formatRomId(rom);
    return true;
}

void logTemperature(const TemperatureData &temperatureData)
{
    Logger::debugf(
        "Temperature probe: %s = %.2f C",
        temperatureData.sensorId.c_str(),
        temperatureData.temperature);
}

int DS18B20Provider::getTemperatures(
    TemperatureData *data,
    int maxCount)
{
    if (data == nullptr || maxCount < 1)
    {
        return 0;
    }

    if (!probeIdInitialized_)
    {
        if (!readProbeId(pin_, probeId_))
        {
            return 0;
        }

        probeIdInitialized_ = true;
        Logger::debugf("Temperature probe detected: %s", probeId_.c_str());
    }

    if (!resetOneWireBus(pin_))
    {
        return 0;
    }

    writeOneWireByte(pin_, SkipRomCommand);
    writeOneWireByte(pin_, ConvertTCommand);
    delay(ConversionDelayMs);

    if (!resetOneWireBus(pin_))
    {
        return 0;
    }

    writeOneWireByte(pin_, SkipRomCommand);
    writeOneWireByte(pin_, ReadScratchpadCommand);

    uint8_t scratchpad[9];
    for (int index = 0; index < 9; ++index)
    {
        scratchpad[index] = readOneWireByte(pin_);
    }

    if (crc8(scratchpad, 8) != scratchpad[8])
    {
        return 0;
    }

    const int16_t rawTemperature = static_cast<int16_t>(
        (static_cast<int16_t>(scratchpad[1]) << 8) | scratchpad[0]);
    const float temperature = static_cast<float>(rawTemperature) / 16.0f;

    data[0] = {probeId_, temperature};
    logTemperature(data[0]);
    return 1;
}

#else

DS18B20Provider::DS18B20Provider(uint8_t pin)
    : pin_(pin), probeId_(), probeIdInitialized_(false)
{
}

int DS18B20Provider::getTemperatures(
    TemperatureData *data,
    int maxCount)
{
    (void)data;
    (void)maxCount;
    (void)pin_;
    (void)probeId_;
    (void)probeIdInitialized_;
    return 0;
}

#endif
