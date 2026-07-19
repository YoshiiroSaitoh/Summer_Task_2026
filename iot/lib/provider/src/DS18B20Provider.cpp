#include "DS18B20Provider.h"

#ifdef ARDUINO
#include <Arduino.h>
#include <Logger.h>
#include <cstdio>

namespace
{
constexpr unsigned long ConversionDelayMs = 750;
constexpr uint8_t SearchRomCommand = 0xF0;
constexpr uint8_t MatchRomCommand = 0x55;
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

bool searchNextRom(
    uint8_t pin,
    uint8_t rom[8],
    int &lastDiscrepancy,
    bool &lastDeviceFlag)
{
    if (lastDeviceFlag)
    {
        return false;
    }

    if (!resetOneWireBus(pin))
    {
        lastDiscrepancy = 0;
        lastDeviceFlag = false;
        return false;
    }

    writeOneWireByte(pin, SearchRomCommand);

    uint8_t idBitNumber = 1;
    uint8_t lastZero = 0;
    uint8_t romByteNumber = 0;
    uint8_t romByteMask = 1;
    bool searchResult = false;

    do
    {
        const bool idBit = readOneWireBit(pin);
        const bool complementIdBit = readOneWireBit(pin);

        if (idBit && complementIdBit)
        {
            break;
        }

        uint8_t searchDirection;
        if (idBit != complementIdBit)
        {
            searchDirection = idBit ? 1 : 0;
        }
        else
        {
            if (idBitNumber < lastDiscrepancy)
            {
                searchDirection = (rom[romByteNumber] & romByteMask) != 0 ? 1 : 0;
            }
            else
            {
                searchDirection = (idBitNumber == lastDiscrepancy) ? 1 : 0;
            }

            if (searchDirection == 0)
            {
                lastZero = idBitNumber;
            }
        }

        if (searchDirection != 0)
        {
            rom[romByteNumber] |= romByteMask;
        }
        else
        {
            rom[romByteNumber] &= static_cast<uint8_t>(~romByteMask);
        }

        writeOneWireBit(pin, searchDirection != 0);

        ++idBitNumber;
        romByteMask <<= 1;
        if (romByteMask == 0)
        {
            ++romByteNumber;
            romByteMask = 1;
        }
    } while (romByteNumber < 8);

    if (idBitNumber >= 65)
    {
        lastDiscrepancy = lastZero;
        if (lastDiscrepancy == 0)
        {
            lastDeviceFlag = true;
        }

        searchResult = true;
    }

    if (!searchResult || crc8(rom, 7) != rom[7])
    {
        return false;
    }

    return true;
}

int discoverProbes(
    uint8_t pin,
    uint8_t probeRoms[][8],
    String *probeIds,
    int maxCount)
{
    int probeCount = 0;
    int lastDiscrepancy = 0;
    bool lastDeviceFlag = false;
    uint8_t rom[8] = {0};

    const bool busPresent = resetOneWireBus(pin);
    Logger::debugf("OneWire bus presence: %s", busPresent ? "detected" : "not detected");
    if (!busPresent)
    {
        return 0;
    }

    while (probeCount < maxCount)
    {
        if (!searchNextRom(pin, rom, lastDiscrepancy, lastDeviceFlag))
        {
            break;
        }

        for (int index = 0; index < 8; ++index)
        {
            probeRoms[probeCount][index] = rom[index];
        }

        probeIds[probeCount] = formatRomId(rom);
        Logger::debugf("Temperature probe detected[%d]: %s", probeCount, probeIds[probeCount].c_str());
        ++probeCount;

        if (lastDeviceFlag)
        {
            break;
        }
    }

    Logger::debugf("Temperature probe discovery finished: %d", probeCount);
    for (int index = 0; index < probeCount; ++index)
    {
        Logger::debugf("Temperature probe[%d] rom: %s", index, probeIds[index].c_str());
    }

    return probeCount;
}

bool readTemperatureForRom(
    uint8_t pin,
    const uint8_t rom[8],
    float &temperature)
{
    if (!resetOneWireBus(pin))
    {
        return false;
    }

    writeOneWireByte(pin, MatchRomCommand);
    for (int index = 0; index < 8; ++index)
    {
        writeOneWireByte(pin, rom[index]);
    }

    writeOneWireByte(pin, ReadScratchpadCommand);

    uint8_t scratchpad[9];
    for (int index = 0; index < 9; ++index)
    {
        scratchpad[index] = readOneWireByte(pin);
    }

    if (crc8(scratchpad, 8) != scratchpad[8])
    {
        return false;
    }

    const int16_t rawTemperature = static_cast<int16_t>(
        (static_cast<int16_t>(scratchpad[1]) << 8) | scratchpad[0]);
    temperature = static_cast<float>(rawTemperature) / 16.0f;
    return true;
}

void logTemperature(const TemperatureData &temperatureData)
{
    Logger::debugf(
        "Temperature probe: %s = %.2f C",
        temperatureData.sensorId.c_str(),
        temperatureData.temperature);
}
}

DS18B20Provider::DS18B20Provider(uint8_t pin)
    : pin_(pin), probeCount_(0), probesInitialized_(false)
{
    for (int probeIndex = 0; probeIndex < AppConfig::MAX_TEMPERATURE_COUNT; ++probeIndex)
    {
        for (int romIndex = 0; romIndex < 8; ++romIndex)
        {
            probeRoms_[probeIndex][romIndex] = 0;
        }
    }
}

int DS18B20Provider::getTemperatures(
    TemperatureData *data,
    int maxCount)
{
    if (data == nullptr || maxCount < 1)
    {
        return 0;
    }

    if (!probesInitialized_)
    {
        const int discoveryAttempts = 3;
        for (int attempt = 0; attempt < discoveryAttempts; ++attempt)
        {
            if (attempt > 0)
            {
                delay(250);
            }

            probeCount_ = discoverProbes(
                pin_,
                probeRoms_,
                probeIds_,
                AppConfig::MAX_TEMPERATURE_COUNT);
            Logger::debugf("Temperature probes discovered: %d", probeCount_);

            if (probeCount_ > 0)
            {
                probesInitialized_ = true;
                break;
            }
        }

        if (probeCount_ <= 0)
        {
            probesInitialized_ = false;
            return 0;
        }
    }

    if (probeCount_ <= 0)
    {
        return 0;
    }

    if (!resetOneWireBus(pin_))
    {
        return 0;
    }

    writeOneWireByte(pin_, SkipRomCommand);
    writeOneWireByte(pin_, ConvertTCommand);
    delay(ConversionDelayMs);

    const int probeLimit = maxCount < probeCount_ ? maxCount : probeCount_;
    int resultCount = 0;
    for (int index = 0; index < probeLimit; ++index)
    {
        float temperature = 0.0f;
        if (!readTemperatureForRom(pin_, probeRoms_[index], temperature))
        {
            Logger::warnf("Failed to read temperature for probe[%d]: %s", index, probeIds_[index].c_str());
            continue;
        }

        data[resultCount] = {probeIds_[index], temperature};
        logTemperature(data[resultCount]);
        ++resultCount;
    }

    Logger::debugf("Temperature probe results: %d/%d", resultCount, probeCount_);
    return resultCount;
}

#else

DS18B20Provider::DS18B20Provider(uint8_t pin)
    : pin_(pin), probeCount_(0), probesInitialized_(false)
{
    for (int probeIndex = 0; probeIndex < AppConfig::MAX_TEMPERATURE_COUNT; ++probeIndex)
    {
        for (int romIndex = 0; romIndex < 8; ++romIndex)
        {
            probeRoms_[probeIndex][romIndex] = 0;
        }
    }
}

int DS18B20Provider::getTemperatures(
    TemperatureData *data,
    int maxCount)
{
    (void)data;
    (void)maxCount;
    (void)pin_;
    (void)probeRoms_;
    (void)probeIds_;
    (void)probeCount_;
    (void)probesInitialized_;
    return 0;
}

#endif
