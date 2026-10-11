package dev.ticketrush;

import io.restassured.RestAssured;
import io.restassured.http.ContentType;
import io.restassured.response.Response;
import org.testng.annotations.BeforeMethod;
import org.testng.annotations.BeforeSuite;

import java.util.Map;

import static io.restassured.RestAssured.given;
import static org.hamcrest.Matchers.emptyOrNullString;
import static org.hamcrest.Matchers.equalTo;
import static org.hamcrest.Matchers.not;

/**
 * Shared setup. The API must be running with ADMIN_ENABLED=true,
 * because every test starts from fresh data via POST /admin/reset.
 */
public abstract class BaseTest {

    protected static final int HOT_SHOW = 1;   // the 120-seat concert

    @BeforeSuite
    public void configureRestAssured() {
        RestAssured.baseURI = System.getProperty("api.baseUri", "http://localhost:8000");
        RestAssured.enableLoggingOfRequestAndResponseIfValidationFails();

        given()
            .get("/health")
        .then()
            .statusCode(200)
            .body("admin_enabled", equalTo(true));
    }

    @BeforeMethod
    public void freshData() {
        resetData(0);
    }

    protected void resetData(int saleOpensInSeconds) {
        given()
            .contentType(ContentType.JSON)
            .body(Map.of("sale_opens_in_seconds", saleOpensInSeconds))
            .post("/admin/reset")
        .then()
            .statusCode(200);
    }

    protected Response reserve(String seatId, String customerId) {
        return given()
            .contentType(ContentType.JSON)
            .body(Map.of("event_id", HOT_SHOW, "seat_id", seatId, "customer_id", customerId))
            .post("/reservations");
    }

    protected Response order(String reservationId) {
        return given()
            .contentType(ContentType.JSON)
            .body(Map.of("reservation_id", reservationId))
            .post("/orders");
    }

    protected void assertError(Response response, int status, String error) {
        response.then()
            .statusCode(status)
            .body("error", equalTo(error))
            .body("message", not(emptyOrNullString()));
    }
}
