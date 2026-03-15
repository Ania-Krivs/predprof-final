export const analyticsMock = {
  epochs_accuracy: [
    { epoch: 1, accuracy: 0.51 },
    { epoch: 2, accuracy: 0.61 },
    { epoch: 3, accuracy: 0.72 },
    { epoch: 4, accuracy: 0.79 },
    { epoch: 5, accuracy: 0.83 }
  ],
  train_class_distribution: {
    class_0: 130,
    class_1: 119,
    class_2: 141,
    class_3: 122,
    class_4: 117
  },
  test_record_accuracy: [
    { record: 1, accuracy: 1 },
    { record: 2, accuracy: 0 },
    { record: 3, accuracy: 1 },
    { record: 4, accuracy: 1 },
    { record: 5, accuracy: 0 }
  ],
  valid_top_5_classes: {
    class_3: 52,
    class_7: 48,
    class_1: 43,
    class_0: 41,
    class_5: 39
  }
};
