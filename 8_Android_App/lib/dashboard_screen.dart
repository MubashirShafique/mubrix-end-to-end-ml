import 'package:android_app/backend.dart';
import 'package:flutter/material.dart';
import 'package:lottie/lottie.dart';

class DashboardScreen extends StatefulWidget {
  const DashboardScreen({super.key});

  @override
  State<DashboardScreen> createState() => _DashboardScreenState();
}

class _DashboardScreenState extends State<DashboardScreen> {
  final List<String> assets = ["bitcoin", "ethereum", "litecoin", "ripple", "gold", "silver"];
  String? selectedAsset = 'bitcoin';
  bool showPrediction = false;
  bool _isConfettiVisible = true;
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.black, // Isse white flash kam hogi
      appBar: AppBar(
        title: const Text("Mubrix Dashboard",style: TextStyle(
          color: Colors.white60
        ),),
        backgroundColor: Colors.black,
        foregroundColor: Colors.white60,
      ),
      body: Stack(
        children:[ Padding(
          padding: const EdgeInsets.all(20.0),
          child: SingleChildScrollView(
            child: Column(
              children: [
                SizedBox(height: 10,),
                DropdownButtonFormField<String>(
                  initialValue: selectedAsset,
                  dropdownColor: Colors.grey[900],
                  style: const TextStyle(color: Colors.white),
                  decoration: InputDecoration(
                    labelText: "Select Asset",
                    labelStyle: const TextStyle(color: Colors.orange),
                    enabledBorder: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(15),
                      borderSide: const BorderSide(color: Colors.deepPurple),
                    ),
                    border: OutlineInputBorder(borderRadius: BorderRadius.circular(15)),
                  ),
                  items: assets.map((String asset) {
                    return DropdownMenuItem<String>(
                      value: asset,
                      child: Text(asset.toUpperCase(),style: TextStyle(
                        color: Colors.orange,
                      ),),
                    );
                  }).toList(),
                  onChanged: (newValue) {
                    setState(() {
                      selectedAsset = newValue;
                    });
                  },
                ),
                const SizedBox(height: 30),
                ElevatedButton(onPressed: (){
                  setState(() {
                    showPrediction = false;
                  });
                  Future.delayed(Duration(milliseconds: 50), () {
                    setState(() {
                      showPrediction = true;
                    });
                  });
            
                },style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.deepPurple,
                  padding: EdgeInsets.symmetric(horizontal: 70, vertical: 15),
                ),child: Text("Predict",style: TextStyle(
                  color: Colors.orange,
            
                ),
                )),
                SizedBox(height: 30,),
                if (showPrediction)  Backend(assetName: selectedAsset!),
            
            
              ],
            ),
          ),
        ),
          if (_isConfettiVisible)
            Align(
              alignment: Alignment.topCenter,
              child: Lottie.asset(
                'assets/animations/Confetti-Animation.json', // File name check karlein
                repeat: false,
                fit: BoxFit.contain,
                onLoaded: (composition) {
                  // Jab animation khatam ho jaye (composition.duration ke baad), ise hide kar dein
                  Future.delayed(composition.duration, () {
                    if (mounted) {
                      setState(() {
                        _isConfettiVisible = false;
                      });
                    }
                  });
                },
              ),
            ),
    ]
      ),
    );
  }
}