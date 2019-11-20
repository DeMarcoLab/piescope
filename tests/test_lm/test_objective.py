import mock
import pytest

from piescope.lm.objective import StageController

# Consider using the pytest-socket plugin here to disable all calls
# The mocket library may also be useful here: https://github.com/mindflayer/python-mocket

@pytest.fixture
def stage():
    stage = StageController(testing=True, timeout=0.5)
    return stage


def test_StageController():
    stage = StageController(testing=True)
    assert stage.timeout == 5.0


def test_graceful_connection_error():
    with pytest.raises(RuntimeError):
        stage = StageController(host='invalid', timeout=0.5)
        assert stage is None


@mock.patch.object(StageController, 'recv')
@mock.patch.object(StageController, 'sendall')
def test_initialise_system_parameters(mock_sendall, mock_recv, stage):
    stage.initialise_system_parameters()


@mock.patch.object(StageController, 'recv')
@mock.patch.object(StageController, 'sendall')
def test_set_relative_accumulation_on(mock_sendall, mock_recv, stage):
    on = 1
    stage.set_relative_accumulation(on)
    cmd = 'SARP0,' + str(on)
    mock_sendall.assert_called_with(bytes(':' + cmd + '\012', 'utf-8'))


@mock.patch.object(StageController, 'recv')
@mock.patch.object(StageController, 'sendall')
def test_set_relative_accumulation_on(mock_sendall, mock_recv, stage):
    off = 0
    stage.set_relative_accumulation(off)
    cmd = 'SARP0,' + str(off)
    mock_sendall.assert_called_with(bytes(':' + cmd + '\012', 'utf-8'))


@mock.patch.object(StageController, 'recv')
@mock.patch.object(StageController, 'sendall')
def test_find_reference_mark(mock_sendall, mock_recv, stage):
    mark = 0  # central reference mark
    hold = 1000
    stage.find_reference_mark(mark, hold=hold)
    cmd = 'FRM0,' + str(mark) + ',' + str(hold) + ',1'
    mock_sendall.assert_called_with(bytes(':' + cmd + '\012', 'utf-8'))


@mock.patch.object(StageController, 'recv')
@mock.patch.object(StageController, 'sendall')
def test_set_start_position(mock_sendall, mock_recv, stage):
    start_position = 200  # in nanometers (must be an integer)
    stage.set_start_position(start_position)
    cmd = 'SP0,' + str(start_position)
    mock_sendall.assert_called_with(bytes(':' + cmd + '\012', 'utf-8'))


@mock.patch.object(StageController, 'recv')
@mock.patch.object(StageController, 'sendall')
def test_move_absolute(mock_sendall, mock_recv, stage):
    mock_sendall.return_value = None
    mock_recv.return_value = None
    distance = 100  # in nanometers (must be an integer)
    hold = 1000     # in milliseconds (must be an integer)
    stage.move_absolute(distance, hold=hold)
    cmd = 'MPA0,' + str(distance) + ',' + str(hold)
    mock_sendall.assert_called_with(bytes(':' + cmd + '\012', 'utf-8'))


@mock.patch.object(StageController, 'recv')
@mock.patch.object(StageController, 'sendall')
def test_move_relative(mock_sendall, mock_recv, stage):
    mock_sendall.return_value = None
    mock_recv.return_value = None
    distance = 100  # in nanometers (must be an integer)
    hold = 1000     # in milliseconds (must be an integer)
    stage.move_relative(distance, hold=hold)
    cmd = 'MPR0,' + str(distance) + ',' + str(hold)
    mock_sendall.assert_called_with(bytes(':' + cmd + '\012', 'utf-8'))


@mock.patch.object(StageController, 'recv')
@mock.patch.object(StageController, 'sendall')
def test_current_position(mock_sendall, mock_recv, stage):
    mock_sendall.return_value = None
    mock_recv.return_value = None
    stage.current_position()
    mock_sendall.assert_called_with(bytes(':' + 'GP0' + '\012', 'utf-8'))


@mock.patch.object(StageController, 'recv')
@mock.patch.object(StageController, 'sendall')
def test_send_command(mock_sendall, mock_recv, stage):
    mock_sendall.return_value = None
    mock_recv.return_value = None
    stage.send_command('command')
    mock_sendall.assert_called_with(bytes(':' + 'command' + '\012', 'utf-8'))


def test_send_command_error(stage):
    with mock.patch.object(StageController, 'sendall', side_effect=Exception):
        with pytest.raises(Exception):
            stage.send_command('command')
