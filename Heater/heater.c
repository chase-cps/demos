/* One step of the thermostat: heat (3 units) while the temperature is
   below 74. */
int thermostat(int T) {
    if (T < 74)
        return 3;
    return 0;
}
