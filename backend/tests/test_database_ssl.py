from app.core.database import build_connect_args


def test_mysql_connect_args_use_ca_and_verify_certificate():
    connect_args = build_connect_args(
        "mysql+pymysql://user:password@192.168.0.189:3306/fg",
        mysql_ssl_ca="/run/secrets/mysql-central-ca.pem",
        mysql_ssl_verify_cert=True,
        mysql_ssl_verify_identity=False,
    )

    assert connect_args["ssl"] == {
        "ca": "/run/secrets/mysql-central-ca.pem",
        "check_hostname": False,
        "verify_mode": 2,
    }
