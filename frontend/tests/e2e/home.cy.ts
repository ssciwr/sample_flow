describe("Home page", () => {
  it("visits the app root url", () => {
    cy.intercept(
      {
        method: "GET",
        url: "/remaining",
      },
      { remaining: 67 }
    );
    cy.visit("/");
    cy.contains("li", "Remaining available samples this week: 67");
  });
});
