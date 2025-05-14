import logging

from pytest import LogCaptureFixture, fixture

from src.ut import Break, catch_break, service


@service
class UpdatePlanSvc:
    plan_id: int

    def run(self):
        return self.plan_id

    @catch_break
    def run_with_capture(self):
        return self.plan_id

    @catch_break
    def run_with_break(self):
        raise Break

    @catch_break
    def run_with_break_reason(self):
        err_msg = "Manual stop."
        raise Break(err_msg)


class TestService:
    @fixture
    def svc(self) -> UpdatePlanSvc:
        return UpdatePlanSvc(plan_id=777)

    def test_service_init(self, caplog: LogCaptureFixture):
        with caplog.at_level(logging.DEBUG):
            UpdatePlanSvc(plan_id=777)

        msg = "Initializing 'UpdatePlanSvc' with args=(), kwargs={'plan_id': 777}"
        assert [msg] == caplog.messages

    def test_run(self):
        plan_id = 777
        svc = UpdatePlanSvc(plan_id=plan_id)

        result = svc.run()

        assert result == plan_id

    def test_run_with_capture(self):
        plan_id = 777
        svc = UpdatePlanSvc(plan_id=plan_id)

        result = svc.run_with_capture()

        assert result == plan_id

    def test_run_with_break(self, svc: UpdatePlanSvc, caplog: LogCaptureFixture):

        with caplog.at_level(logging.DEBUG):
            result = svc.run_with_break()

        assert result is None
        msg = "Break svc operation. Reason: 'Reason not provided'"
        assert [msg] == caplog.messages

    def test_capture_break_without_reason(
        self, svc: UpdatePlanSvc, caplog: LogCaptureFixture
    ):
        with caplog.at_level(logging.DEBUG):
            result = svc.run_with_break_reason()

        assert result is None
        msg = "Break svc operation. Reason: 'Manual stop.'"
        assert [msg] == caplog.messages
