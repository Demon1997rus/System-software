set(TARGET testirovka)

qt_add_executable(${TARGET} pthread zmq rt boost_random boost_unit_test_framework boost_system)
