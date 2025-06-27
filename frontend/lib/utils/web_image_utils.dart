import 'package:flutter/foundation.dart';
import 'package:image_picker/image_picker.dart';

class WebImageUtils {
  static Future<XFile?> pickImage() async {
    final ImagePicker picker = ImagePicker();
    
    try {
      final XFile? image = await picker.pickImage(
        source: ImageSource.gallery,
        maxWidth: 512,
        maxHeight: 512,
        imageQuality: 75,
      );
      
      return image;
    } catch (e) {
      if (kDebugMode) {
        print('Error picking image: $e');
      }
      rethrow;
    }
  }

  static Future<Uint8List?> getImageBytes(XFile? image) async {
    if (image == null) return null;
    
    try {
      return await image.readAsBytes();
    } catch (e) {
      if (kDebugMode) {
        print('Error reading image bytes: $e');
      }
      return null;
    }
  }
}
