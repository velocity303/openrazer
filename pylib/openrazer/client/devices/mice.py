import dbus as _dbus

from openrazer.client.devices import RazerDevice as __RazerDevice
from openrazer.client.macro import RazerMacro as _RazerMacro
from openrazer.client import constants as _c


class RazerMouse(__RazerDevice):
    _MACRO_CLASS = _RazerMacro

    @property
    def max_dpi(self) -> int:
        """
        Gets max DPI

        :return: Max DPI, if device does not have DPI it'll return None
        :rtype: int or None
        """
        if self.has('dpi'):
            return int(self._dbus_interfaces['dpi'].maxDPI())
        else:
            return None

    @property
    def available_dpi(self) -> list:
        """
        Gets the available DPI

        :return: Available DPI, if device has only a couple of fixed possible DPI values
        :rtype: list or None
        """
        if self.has('available_dpi'):
            dbuslist = self._dbus_interfaces['dpi'].availableDPI()
            # Repack list from dbus ints to normal ints
            return [int(d) for d in dbuslist]
        else:
            return None

    @property
    def dpi(self) -> tuple:
        """
        Get mouse DPI

        Will return a tuple
        :return: DPI (500, 500)
        :rtype: tuple

        :raises NotImplementedError: If function is not supported
        """
        if self.has('available_dpi'):
            dpi_x = self._dbus_interfaces['dpi'].getDPI()[0]
            return int(dpi_x), 0
        elif self.has('dpi'):
            dpi_x, dpi_y = self._dbus_interfaces['dpi'].getDPI()
            # Converting to integers to remove the dbus types
            return int(dpi_x), int(dpi_y)
        else:
            raise NotImplementedError()

    @dpi.setter
    def dpi(self, value: tuple):
        """
        Set mouse dpi

        Daemon does type validation but can't be too careful
        :param value: DPI X, Y tuple
        :type value: tuple

        :raises ValueError: If the tuple isn't long enough or contains invalid crap
        :raises NotImplementedError: If function is not supported
        """
        if self.has('dpi'):
            if len(value) != 2:
                raise ValueError("DPI tuple is not of length 2. Length: {0}".format(len(value)))
            max_dpi = self.max_dpi
            dpi_x, dpi_y = value
            dpi_x_only = self.has('available_dpi')

            if not isinstance(dpi_x, int) or not isinstance(dpi_y, int):
                raise ValueError("DPI X or Y is not an integer, X:{0} Y:{1}".format(type(dpi_x), type(dpi_y)))

            if dpi_x < 0 or dpi_x > max_dpi:
                raise ValueError("DPI X either too small or too large, X:{0}".format(dpi_x))

            if dpi_x_only and not dpi_y == 0:
                raise ValueError("DPI Y is not supported for this device")
            elif dpi_y < 0 or dpi_y > max_dpi:
                raise ValueError("DPI Y either too small or too large, Y:{0}".format(dpi_y))

            self._dbus_interfaces['dpi'].setDPI(dpi_x, dpi_y)
        else:
            raise NotImplementedError()

    @property
    def dpi_stages(self) -> (int, list):
        """
        Get mouse DPI stages

        Will return a tuple containing the active DPI stage number and the list
        of DPI stages as tuples.
        The active DPI stage number must be: >= 1 and <= nr of DPI stages.
        :return: active DPI stage number and DPI stages
                 (1, [(500, 500), (1000, 1000), (2000, 2000) ...]
        :rtype: (int, list)

        :raises NotImplementedError: if function is not supported
        """
        if self.has('dpi_stages'):
            response = self._dbus_interfaces['dpi'].getDPIStages()
            dpi_stages = []

            active_stage = int(response[0])

            for dpi_x, dpi_y in response[1]:
                dpi_stages.append((int(dpi_x), int(dpi_y)))

            return (active_stage, dpi_stages)
        else:
            raise NotImplementedError()

    @dpi_stages.setter
    def dpi_stages(self, value: (int, list)):
        """
        Set mouse DPI stages

        Daemon does type validation but can't be too careful
        :param value: active DPI stage number and list of DPI X, Y tuples
        :type value: (int, list)

        :raises ValueError: when the input is invalid
        :raises NotImplementedError: If function is not supported
        """
        if self.has('dpi_stages'):
            max_dpi = self.max_dpi
            dpi_stages = []

            active_stage = value[0]
            if not isinstance(active_stage, int):
                raise ValueError(
                    "Active DPI stage is not an integer: {0}".format(
                        type(active_stage)))

            if active_stage < 1:
                raise ValueError(
                    "Active DPI stage has invalid value: {0} < 1".format(
                        active_stage))

            for stage in value[1]:
                if len(stage) != 2:
                    raise ValueError(
                        "DPI tuple is not of length 2. Length: {0}".format(
                            len(stage)))

                dpi_x, dpi_y = stage

                if not isinstance(dpi_x, int) or not isinstance(dpi_y, int):
                    raise ValueError(
                        "DPI X or Y is not an integer, X:{0} Y:{1}".format(
                            type(dpi_x), type(dpi_y)))

                if dpi_x < 0 or dpi_x > max_dpi:
                    raise ValueError(
                        "DPI X either too small or too large, X:{0}".format(
                            dpi_x))
                if dpi_y < 0 or dpi_y > max_dpi:
                    raise ValueError(
                        "DPI Y either too small or too large, Y:{0}".format(
                            dpi_y))

                dpi_stages.append((dpi_x, dpi_y))

            if active_stage > len(dpi_stages):
                raise ValueError(
                    "Active DPI stage has invalid value: {0} > {1}".format(
                        active_stage, len(dpi_stages)))

            self._dbus_interfaces['dpi'].setDPIStages(active_stage, dpi_stages)
        else:
            raise NotImplementedError()

    @property
    def poll_rate(self) -> int:
        """
        Get poll rate from device

        :return: Poll rate
        :rtype: int

        :raises NotImplementedError: If function is not supported
        """
        if self.has('poll_rate'):
            return int(self._dbus_interfaces['device'].getPollRate())
        else:
            raise NotImplementedError()

    @poll_rate.setter
    def poll_rate(self, poll_rate: int):
        """
        Set poll rate of device

        :param poll_rate: Polling rate
        :type poll_rate: int

        :raises NotImplementedError: If function is not supported
        """
        if self.has('poll_rate'):
            if not isinstance(poll_rate, int):
                raise ValueError("Poll rate is not an integer: {0}".format(poll_rate))
            if poll_rate not in (_c.POLL_125HZ, _c.POLL_500HZ, _c.POLL_1000HZ):
                raise ValueError('Poll rate "{0}" is not one of {1}'.format(poll_rate, (_c.POLL_125HZ, _c.POLL_500HZ, _c.POLL_1000HZ)))

            self._dbus_interfaces['device'].setPollRate(poll_rate)

        else:
            raise NotImplementedError()
