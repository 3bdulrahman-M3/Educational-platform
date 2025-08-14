# Cloudinary Frontend Configuration

## 🔑 **Cloudinary Credentials**

Here are the Cloudinary credentials you need for frontend integration:

```javascript
const CLOUDINARY_CONFIG = {
  cloud_name: "ddtp8tqvv",
  api_key: "272766425297671",
  api_secret: "o44U57Jmn3Rjtz_N2SDrpS7Mow0",
  upload_preset: "ml_default", // You may need to create this in your Cloudinary dashboard
};
```

## 📦 **Frontend Integration Options**

### Option 1: Direct Upload to Cloudinary (Recommended)

**Install Cloudinary SDK:**

```bash
# For React/Vue/Angular
npm install cloudinary

# For vanilla JavaScript
npm install cloudinary-core
```

**React Example:**

```javascript
import { Cloudinary } from "cloudinary-core";

const cloudinary = new Cloudinary({
  cloud_name: "ddtp8tqvv",
  api_key: "272766425297671",
  api_secret: "o44U57Jmn3Rjtz_N2SDrpS7Mow0",
});

// Upload image directly to Cloudinary
const uploadImage = async (file) => {
  const formData = new FormData();
  formData.append("file", file);
  formData.append("upload_preset", "ml_default"); // Create this preset in Cloudinary dashboard
  formData.append("cloud_name", "ddtp8tqvv");

  try {
    const response = await fetch(
      `https://api.cloudinary.com/v1_1/ddtp8tqvv/image/upload`,
      {
        method: "POST",
        body: formData,
      }
    );
    const data = await response.json();
    return data.secure_url; // Returns the uploaded image URL
  } catch (error) {
    console.error("Upload failed:", error);
    throw error;
  }
};

// Usage in component
const handleImageUpload = async (event) => {
  const file = event.target.files[0];
  if (file) {
    try {
      const imageUrl = await uploadImage(file);
      console.log("Uploaded image URL:", imageUrl);
      // Now send this URL to your Django API
      await createCourse({
        title: "My Course",
        description: "Course description",
        image: imageUrl,
      });
    } catch (error) {
      console.error("Upload failed:", error);
    }
  }
};
```

**Vue.js Example:**

```javascript
// In your Vue component
export default {
  data() {
    return {
      cloudinaryConfig: {
        cloud_name: "ddtp8tqvv",
        api_key: "272766425297671",
        api_secret: "o44U57Jmn3Rjtz_N2SDrpS7Mow0",
      },
    };
  },
  methods: {
    async uploadImage(file) {
      const formData = new FormData();
      formData.append("file", file);
      formData.append("upload_preset", "ml_default");
      formData.append("cloud_name", "ddtp8tqvv");

      try {
        const response = await fetch(
          "https://api.cloudinary.com/v1_1/ddtp8tqvv/image/upload",
          {
            method: "POST",
            body: formData,
          }
        );
        const data = await response.json();
        return data.secure_url;
      } catch (error) {
        console.error("Upload failed:", error);
        throw error;
      }
    },
    async handleImageUpload(event) {
      const file = event.target.files[0];
      if (file) {
        try {
          const imageUrl = await this.uploadImage(file);
          this.course.image = imageUrl;
        } catch (error) {
          this.$toast.error("Image upload failed");
        }
      }
    },
  },
};
```

**Angular Example:**

```typescript
// In your Angular service
import { Injectable } from "@angular/core";
import { HttpClient } from "@angular/common/http";

@Injectable({
  providedIn: "root",
})
export class CloudinaryService {
  private readonly CLOUDINARY_URL =
    "https://api.cloudinary.com/v1_1/ddtp8tqvv/image/upload";
  private readonly CLOUD_NAME = "ddtp8tqvv";
  private readonly UPLOAD_PRESET = "ml_default";

  constructor(private http: HttpClient) {}

  uploadImage(file: File): Promise<string> {
    const formData = new FormData();
    formData.append("file", file);
    formData.append("upload_preset", this.UPLOAD_PRESET);
    formData.append("cloud_name", this.CLOUD_NAME);

    return this.http
      .post<any>(this.CLOUDINARY_URL, formData)
      .toPromise()
      .then((response) => response.secure_url);
  }
}

// In your component
export class CourseComponent {
  constructor(
    private cloudinaryService: CloudinaryService,
    private courseService: CourseService
  ) {}

  async onImageSelected(event: any) {
    const file = event.target.files[0];
    if (file) {
      try {
        const imageUrl = await this.cloudinaryService.uploadImage(file);
        this.courseForm.patchValue({ image: imageUrl });
      } catch (error) {
        console.error("Upload failed:", error);
      }
    }
  }
}
```

### Option 2: Using Cloudinary Widget

**HTML Setup:**

```html
<!-- Add Cloudinary Widget script -->
<script
  src="https://upload-widget.cloudinary.com/global/all.js"
  type="text/javascript"
></script>
```

**JavaScript Implementation:**

```javascript
// Initialize Cloudinary Widget
const myWidget = cloudinary.createUploadWidget(
  {
    cloudName: "ddtp8tqvv",
    uploadPreset: "ml_default",
    sources: ["local", "camera", "url"],
    multiple: false,
    maxFiles: 1,
    resourceType: "image",
    clientAllowedFormats: ["jpg", "jpeg", "png", "gif", "webp"],
    maxFileSize: 10000000, // 10MB
    styles: {
      palette: {
        window: "#FFFFFF",
        windowBorder: "#90A0B3",
        tabIcon: "#0078FF",
        menuIcons: "#5A616A",
        textDark: "#000000",
        textLight: "#FFFFFF",
        link: "#0078FF",
        action: "#FF620C",
        inactiveTabIcon: "#0E2F5A",
        error: "#F44235",
        inProgress: "#0078FF",
        complete: "#20B832",
        sourceBg: "#E4EBF1",
      },
    },
  },
  (error, result) => {
    if (!error && result && result.event === "success") {
      console.log("Upload successful:", result.info.secure_url);
      // Use the uploaded image URL
      document.getElementById("imageUrl").value = result.info.secure_url;
    }
  }
);

// Open widget
document.getElementById("uploadButton").addEventListener("click", () => {
  myWidget.open();
});
```

### Option 3: Vanilla JavaScript with Fetch

```javascript
class CloudinaryUploader {
  constructor() {
    this.cloudName = "ddtp8tqvv";
    this.uploadPreset = "ml_default";
  }

  async uploadImage(file) {
    const formData = new FormData();
    formData.append("file", file);
    formData.append("upload_preset", this.uploadPreset);
    formData.append("cloud_name", this.cloudName);

    try {
      const response = await fetch(
        `https://api.cloudinary.com/v1_1/${this.cloudName}/image/upload`,
        {
          method: "POST",
          body: formData,
        }
      );

      if (!response.ok) {
        throw new Error(`Upload failed: ${response.statusText}`);
      }

      const data = await response.json();
      return {
        url: data.secure_url,
        publicId: data.public_id,
        width: data.width,
        height: data.height,
      };
    } catch (error) {
      console.error("Upload error:", error);
      throw error;
    }
  }

  // Generate optimized image URL
  getOptimizedUrl(publicId, options = {}) {
    const defaultOptions = {
      width: 400,
      height: 300,
      crop: "fill",
      quality: "auto",
      format: "auto",
    };

    const opts = { ...defaultOptions, ...options };
    return `https://res.cloudinary.com/${this.cloudName}/image/upload/c_${opts.crop},w_${opts.width},h_${opts.height},q_${opts.quality},f_${opts.format}/${publicId}`;
  }
}

// Usage
const uploader = new CloudinaryUploader();

document
  .getElementById("imageInput")
  .addEventListener("change", async (event) => {
    const file = event.target.files[0];
    if (file) {
      try {
        const result = await uploader.uploadImage(file);
        console.log("Uploaded:", result.url);

        // Create course with the image URL
        const courseData = {
          title: "My Course",
          description: "Course description",
          image: result.url,
        };

        // Send to your Django API
        await fetch("/api/courses/create/", {
          method: "POST",
          headers: {
            Authorization: `Bearer ${localStorage.getItem("token")}`,
            "Content-Type": "application/json",
          },
          body: JSON.stringify(courseData),
        });
      } catch (error) {
        console.error("Failed to upload:", error);
      }
    }
  });
```

## 🔧 **Environment Variables (Recommended)**

For security, store these in environment variables:

```javascript
// .env file
REACT_APP_CLOUDINARY_CLOUD_NAME = ddtp8tqvv;
REACT_APP_CLOUDINARY_API_KEY = 272766425297671;
REACT_APP_CLOUDINARY_UPLOAD_PRESET = ml_default;

// Usage
const config = {
  cloudName: process.env.REACT_APP_CLOUDINARY_CLOUD_NAME,
  apiKey: process.env.REACT_APP_CLOUDINARY_API_KEY,
  uploadPreset: process.env.REACT_APP_CLOUDINARY_UPLOAD_PRESET,
};
```

## 📸 **Image Transformation Examples**

```javascript
// Thumbnail generation
const thumbnailUrl = `https://res.cloudinary.com/ddtp8tqvv/image/upload/c_thumb,w_200,h_200/${publicId}`;

// Responsive image
const responsiveUrl = `https://res.cloudinary.com/ddtp8tqvv/image/upload/c_scale,w_auto,dpr_auto/${publicId}`;

// Quality optimization
const optimizedUrl = `https://res.cloudinary.com/ddtp8tqvv/image/upload/q_auto,f_auto/${publicId}`;

// Format conversion
const webpUrl = `https://res.cloudinary.com/ddtp8tqvv/image/upload/f_webp/${publicId}`;
```

## 🚨 **Important Security Notes**

1. **API Secret**: Never expose the API secret in frontend code
2. **Upload Preset**: Create an unsigned upload preset in your Cloudinary dashboard
3. **CORS**: Configure CORS settings in Cloudinary dashboard if needed
4. **File Validation**: Always validate file types and sizes on both frontend and backend

## 📋 **Upload Preset Setup**

1. Go to your Cloudinary Dashboard
2. Navigate to Settings > Upload
3. Scroll to Upload presets
4. Create a new preset named `ml_default`
5. Set it to "Unsigned" for frontend uploads
6. Configure allowed formats, sizes, and transformations

This configuration will allow your frontend to upload images directly to Cloudinary and then send the resulting URL to your Django API for course creation.
