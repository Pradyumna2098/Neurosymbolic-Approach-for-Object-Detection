# Frontend Subproject

This subproject will contain web-based dashboards and visual interfaces for monitoring and showcasing results.

## Planned Features

- **Detection Visualization**: Interactive display of object detection results with bounding boxes
- **Knowledge Graph Explorer**: Visual exploration of extracted spatial relationships
- **Performance Dashboard**: Real-time metrics and training progress monitoring
- **Model Comparison**: Side-by-side comparison of different model versions
- **Dataset Browser**: Browse and search training/validation datasets
- **Pipeline Control**: UI for configuring and triggering pipeline runs

## Technology Stack (Planned)

Choose one of:
- **React** with TypeScript + Vite
- **Vue.js** 3 with Composition API
- **Streamlit** (for rapid prototyping)

Additional libraries:
- **Visualization**: D3.js, Plotly, or Recharts
- **State Management**: Redux/Zustand (React) or Pinia (Vue)
- **UI Components**: Material-UI, Ant Design, or shadcn/ui
- **API Client**: Axios or Fetch API

## Getting Started

This subproject is currently a placeholder. Implementation is planned for future releases.

### Proposed Page Structure

```
/
├── /dashboard              # Main dashboard with overview metrics
├── /models
│   ├── /list              # List of trained models
│   └── /details/:id       # Model details and performance
├── /predictions
│   ├── /list              # Prediction results list
│   └── /viewer/:id        # Interactive prediction viewer
├── /knowledge-graph
│   └── /explorer          # Knowledge graph visualization
├── /datasets
│   └── /browser           # Dataset exploration
└── /settings              # Configuration management
```

## Development

When implementing, ensure to:
1. Responsive design for desktop and mobile
2. Accessible UI following WCAG guidelines
3. Dark mode support
4. Efficient rendering for large datasets
5. Real-time updates using WebSockets or Server-Sent Events
6. Comprehensive error handling and user feedback

## Mock UI Ideas

### Detection Viewer
- Image canvas with overlaid bounding boxes
- Color-coded by class
- Confidence scores on hover
- Filter by class, confidence threshold
- Compare original vs. NMS-filtered vs. symbolically-refined predictions

### Knowledge Graph Explorer
- Force-directed graph layout
- Node size proportional to detection frequency
- Edge thickness proportional to co-occurrence weight
- Zoom, pan, and search functionality
- Export to various formats

### Metrics Dashboard
- Training loss curves
- Validation mAP over time
- Class-wise performance breakdown
- Confusion matrices
- Interactive filtering and date range selection

## Related Subprojects

- **Backend**: Provides APIs that frontend will consume
- **Pipeline**: Core logic whose results the frontend displays
- **Monitoring**: Metrics that populate the dashboards
