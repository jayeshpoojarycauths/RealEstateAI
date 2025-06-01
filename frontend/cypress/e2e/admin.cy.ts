describe('Admin Flow', () => {
    beforeEach(() => {
        // Login as admin before each test
        cy.login('admin@example.com', 'admin123');
    });

    it('should manage properties', () => {
        // Navigate to properties page
        cy.visit('/properties');

// Add new property
         cy.get('[data-testid="add-property-button"]').click();
        cy.get('[data-testid="property-form"]').should('be.visible');
         cy.get('[data-testid="property-title"]').type('Test Property');
         cy.get('[data-testid="property-address"]').type('123 Test St');
         cy.get('[data-testid="property-price"]').type('500000');
         cy.get('[data-testid="property-status"]').select('available');
         cy.get('[data-testid="property-type"]').select('residential');
         cy.get('[data-testid="property-area"]').type('2000');
         cy.get('[data-testid="property-submit"]').click();
        cy.get('[data-testid="success-message"]').should('be.visible');

         // Verify property was added
         cy.contains('Test Property').should('be.visible');
        cy.contains('123 Test St').should('be.visible');
        cy.contains('$500,000').should('be.visible');

        // Edit property
        cy.get('[data-testid="edit-property-button"]').first().click();
        cy.get('[data-testid="property-price"]').clear().type('550000');
        cy.get('[data-testid="property-submit"]').click();

        // Verify property was updated
        cy.contains('$550,000').should('be.visible');

        // Delete property
        cy.get('[data-testid="delete-property-button"]').first().click();
        cy.get('[data-testid="confirm-delete"]').click();

        // Verify property was deleted
        cy.contains('Test Property').should('not.exist');
    });

    it('should view audit logs', () => {
        // Navigate to audit logs page
        cy.visit('/admin/audit-logs');

        // Verify audit logs table
        cy.get('[data-testid="audit-logs-table"]').should('be.visible');

        // Test filters
        cy.get('[data-testid="audit-log-search"]').type('property');
        cy.get('[data-testid="audit-log-action-filter"]').select('create');
        cy.get('[data-testid="audit-log-resource-filter"]').select('property');

        // Verify filtered results
        cy.get('[data-testid="audit-log-row"]').should('have.length.at.least', 1);

        // Test pagination
        cy.get('[data-testid="next-page"]').click();
        cy.get('[data-testid="audit-log-row"]').should('be.visible');
    });

    it('should manage user settings', () => {
        // Navigate to settings page
        cy.visit('/settings');

        // Update profile information
        cy.get('[data-testid="first-name"]').clear().type('Admin');
        cy.get('[data-testid="last-name"]').clear().type('User');
        cy.get('[data-testid="phone"]').clear().type('1234567890');

        // Update preferences
        cy.get('[data-testid="language"]').select('en');
        cy.get('[data-testid="theme"]').select('dark');

        // Update notifications
        cy.get('[data-testid="email-notifications"]').click();
        cy.get('[data-testid="sms-notifications"]').click();

        // Save changes
        cy.get('[data-testid="save-settings"]').click();

        // Verify success message
        cy.contains('Settings updated successfully').should('be.visible');

        // Verify changes persisted
        cy.reload();
        cy.get('[data-testid="first-name"]').should('have.value', 'Admin');
        cy.get('[data-testid="last-name"]').should('have.value', 'User');
        cy.get('[data-testid="phone"]').should('have.value', '1234567890');
        cy.get('[data-testid="language"]').should('have.value', 'en');
        cy.get('[data-testid="theme"]').should('have.value', 'dark');
    });
}); 