from pathlib import Path

from ..programs import gaussian


def get_scf_lines():
    file_path = Path(__file__).with_name("gau_out.dat")
    with file_path.open("r") as file:
        return file.readlines()


lines = get_scf_lines()
gau = gaussian.GaussianHarness(lines)


def test_energy():
    result = gau.get_energy()  # Call the function you want to test
    assert (
        result == -169.973195608
    )  # Add assertions to check if the result is as expected


def test_scf_cyles():
    result = gau.get_scf_cycles()  # Call the function you want to test
    assert result == 13  # Add assertions to check if the result is as expected


def test_rx_coord():
    result = gau.get_rx_coord()  # Call the function you want to test
    assert result == -2.58535  # Add assertions to check if the result is as expected


def test_occ_orbitals():
    result = gau.get_occ_orbitals()  # Call the function you want to test

    assert result[0] == -19.09953
    assert result[-1] == -0.27034
    assert result[7] == -0.49087

    # Add assertions to check if the result is as expected


def test_virt_orbitals():
    result = gau.get_virt_orbitals()  # Call the function you want to test

    assert result[0] == 0.00813
    assert result[7] == 0.25205
    assert result[-1] == 43.73942


def test_xyz_coords():
    result = gau.get_xyz_coords()  # Call the function you want to test

    assert result[0] == -0.02269
    assert result[7] == -0.33584
    assert result[-1] == 0.0


def test_get_atms_num():
    result = gau.get_atm_num()  # Call the function you want to test

    assert result[0] == 6.0
    assert result[2] == 7.0
    assert result[-1] == 1.0
