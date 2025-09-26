#### 💎 You can please access the service at [photos.nyvs.me](photos.nyvs.me) 💎

## New Features Added ✨
1.  Custom View Limits
-   Choose between 1, 3, 5, 10 views, or unlimited (for 24 hours)
-   Photos still auto-delete after 24 hours regardless

2.  PIN Protection
-   Optional 4-digit PIN
-   Viewers must enter PIN to see the photo
-   PIN is hashed for security

3.  Download Prevention
-   Disables right-click context menu
-   Prevents drag-and-drop

## The New Flow 👩‍💻

-  Upload Page: Select photo → Configure options → Upload
-  Share: Copy the generated URL
-  View Page:

    - If PIN protected → Enter PIN first
    - Photo displays with remaining view count
    - If download prevented → Right-click disabled

## Architecture Overview 🏗️

-  **Upload**: User uploads image → Server stores in S3 temporarily → Returns unique one-time URL
-  **Access**: Someone visits URL → Server fetches from S3 → Serves image → Immediately deletes from S3 and invalidates URL
-  **Security**: URLs use random tokens (not predictable S3 URLs)
