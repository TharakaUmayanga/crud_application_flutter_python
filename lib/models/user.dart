class User {
  final int? id;
  final String name;
  final String email;
  final String? phoneNumber;
  final String? address;
  final int? age;
  final String? profilePicture;

  User({
    this.id,
    required this.name,
    required this.email,
    this.phoneNumber,
    this.address,
    this.age,
    this.profilePicture,
  });

  factory User.fromJson(Map<String, dynamic> json) {
    return User(
      id: json['id'],
      name: json['name'],
      email: json['email'],
      phoneNumber: json['phone_number'],
      address: json['address'],
      age: json['age'],
      profilePicture: json['profile_picture'],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'name': name,
      'email': email,
      'phone_number': phoneNumber,
      'address': address,
      'age': age,
      'profile_picture': profilePicture,
    };
  }

  User copyWith({
    int? id,
    String? name,
    String? email,
    String? phoneNumber,
    String? address,
    int? age,
    String? profilePicture,
  }) {
    return User(
      id: id ?? this.id,
      name: name ?? this.name,
      email: email ?? this.email,
      phoneNumber: phoneNumber ?? this.phoneNumber,
      address: address ?? this.address,
      age: age ?? this.age,
      profilePicture: profilePicture ?? this.profilePicture,
    );
  }
}
