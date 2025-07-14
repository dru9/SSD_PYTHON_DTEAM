from pytest_mock import MockerFixture


def test_ssd_read(mocker: MockerFixture):
    ssd = mocker.Mock()
    data = [idx + 123 for idx in range(100)]
    with open("ssd_nand.txt", "w") as f:
        for idx in range(100):
            f.writelines(f"{idx:02d}\t0x{data[idx]:08x}\n")

    with open("ssd_nand.txt", "r") as f:
        while True:
            line = f.readline().split()
            if not line:
                break
            print(line)

