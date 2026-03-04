## Context
Django's default `User` model uses a username as the primary identifier.
ForenLIMS requires email-based authentication for the current development
environment, as email is a universally available identifier that requires
no additional infrastructure.

In production, authentication will likely be delegated to institutional
identity providers (Shibboleth SSO or LDAP/Active Directory), where the
primary identifier may be a institutional username rather than email.
The custom model provides the flexibility to adapt to this without
depending on a third-party model.

## Consequences
...
- Authentication backend may be replaced or extended with
  Shibboleth/LDAP/AD integration in production — django-allauth
  supports custom backends and social providers that can handle this
- The `email` field remains the primary identifier for now but may
  need to be supplemented with an `institutional_username` field
  when SSO integration is implemented — see Open Questions

## Open Questions
- SSO/LDAP integration strategy for production deployment
- Whether email or institutional username becomes the primary
  identifier after SSO integration
- Which additional domain-specific fields will be needed
  (e.g. professional title, department, digital signature)?
- These will be addressed when the organizational structure
  data model is defined
