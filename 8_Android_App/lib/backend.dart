import 'dart:convert';
import 'dart:ui';
import 'package:fl_chart/fl_chart.dart';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:lottie/lottie.dart';

import 'news_Screen.dart';

class Backend extends StatefulWidget {
  final String assetName;

  const Backend({super.key, required this.assetName});

  @override
  State<Backend> createState() => _BackendState();
}

class _BackendState extends State<Backend> {
  String prediction = "0";
  List<dynamic> graphData = [];
  double? confidence;
  bool isLoading = true;
  String? displayedAsset;
  bool isnewsbuttonShow=false;

  @override
  void initState() {
    super.initState();
    fetchPrediction();
  }

  Future<void> fetchPrediction() async {
    setState(() { isLoading = true;isnewsbuttonShow=false;});
    try {
      await Future.delayed(const Duration(seconds: 2));

      const String url = "http://10.0.2.2:8000/predict";
      final response = await http.post(
        Uri.parse(url),
        headers: {"Content-Type": "application/json; charset=UTF-8"},
        body: jsonEncode({"asset": widget.assetName}),
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        setState(() {
          prediction = data['prediction'].toString();
          graphData = data['graph_data'];
          confidence = data['confidence']?.toDouble() ?? 0.0;
          isLoading = false;
          displayedAsset = widget.assetName;
          isnewsbuttonShow=true;
        });
      } else {
        setState(() => isLoading = false);
      }
    } catch (e) {
      setState(() => isLoading = false);
      debugPrint("Connection Error: $e");
    }
  }

  Widget buildAttractiveGraph() {
    return Container(
      height: 300,
      padding: const EdgeInsets.fromLTRB(10, 20, 20, 10),
      child: LineChart(
        LineChartData(
          lineTouchData: LineTouchData(
            touchTooltipData: LineTouchTooltipData(
              getTooltipColor: (touchedSpot) =>
                  Colors.deepPurple.withValues(alpha: 0.8),
              getTooltipItems: (List<LineBarSpot> touchedSpots) {
                return touchedSpots.map((spot) {
                  return LineTooltipItem(
                    '\$${spot.y.toStringAsFixed(2)}\n',
                    const TextStyle(
                      color: Colors.white,
                      fontWeight: FontWeight.bold,
                    ),
                    children: [
                      TextSpan(
                        text: graphData[spot.x.toInt()]['date'],
                        style: const TextStyle(
                          color: Colors.orange,
                          fontSize: 10,
                        ),
                      ),
                    ],
                  );
                }).toList();
              },
            ),
          ),
          gridData: const FlGridData(show: true, drawVerticalLine: false),
          titlesData: FlTitlesData(
            rightTitles: const AxisTitles(
              sideTitles: SideTitles(showTitles: false),
            ),
            topTitles: const AxisTitles(
              sideTitles: SideTitles(showTitles: false),
            ),
            leftTitles: const AxisTitles(
              sideTitles: SideTitles(showTitles: false),
            ),
            bottomTitles: AxisTitles(
              sideTitles: SideTitles(
                showTitles: false,
                reservedSize: 35,
                interval: (graphData.length / 5).toDouble(),
                getTitlesWidget: (double value, TitleMeta meta) {
                  int index = value.toInt();
                  if (index >= 0 && index < graphData.length) {
                    String dateStr = graphData[index]['date'].toString();
                    List<String> dateParts = dateStr.split('-');
                    String shortDate = dateParts.length > 1
                        ? dateParts.skip(1).join('-')
                        : dateStr;

                    return SideTitleWidget(
                      meta: meta,
                      space: 8.0,
                      child: Text(
                        shortDate,
                        style: const TextStyle(
                          color: Colors.white38,
                          fontSize: 10,
                        ),
                      ),
                    );
                  }
                  return const SizedBox();
                },
              ),
            ),
          ),
          borderData: FlBorderData(show: false),
          lineBarsData: [
            LineChartBarData(
              spots: graphData.asMap().entries.map((e) {
                return FlSpot(
                  e.key.toDouble(),
                  (e.value['final_price'] as num).toDouble(),
                );
              }).toList(),
              isCurved: true,
              preventCurveOverShooting: true,
              color: Colors.purple,
              barWidth: 4,
              isStrokeCapRound: true,
              dotData: const FlDotData(show: false),
              belowBarData: BarAreaData(
                show: true,
                gradient: LinearGradient(
                  colors: [
                    Colors.purple.withValues(alpha: 0.3),
                    Colors.purple.withValues(alpha: 0.01),
                  ],
                  begin: Alignment.topCenter,
                  end: Alignment.bottomCenter,
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        Card(
          clipBehavior: Clip.antiAlias,
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(15)),
          child: Container(

            decoration: BoxDecoration(
              gradient: isLoading
                  ? LinearGradient(colors: [Colors.yellow.withValues(alpha: 0.3), Colors.yellow.withValues(alpha: 0.1)])
                  : prediction == "1"
                  ? LinearGradient(colors: [Colors.green.withValues(alpha: 0.5), Colors.green.withValues(alpha: 0.2)])
                  : prediction == "0"
                  ? LinearGradient(colors: [Colors.red.withValues(alpha: 0.5), Colors.red.withValues(alpha: 0.2)])
                  : LinearGradient(colors: [Colors.grey.withValues(alpha: 0.3), Colors.black.withValues(alpha: 0.1)]),
            ),
            child: BackdropFilter(
              filter: ImageFilter.blur(sigmaX: 10, sigmaY: 10),
              child: Padding(
                padding: const EdgeInsets.all(15.0),
                child: isLoading
                    ? Column(
                  children: [
                    Lottie.asset('assets/animations/loading.json', height: 150),
                    const SizedBox(height: 10),
                    const Text(
                      "Processing...",
                      style: TextStyle(color: Colors.purple, fontWeight: FontWeight.bold), // Purple text
                    ),
                  ],
                )
                    : Column(
                  children: [
                    Center(
                      child: Image.asset(
                        'assets/coins_pics/${displayedAsset}.png',
                        height: 100,
                      ),
                    ),
                    const SizedBox(height: 10),
                    Text(
                      "${displayedAsset?.toUpperCase()}",
                      style: const TextStyle(
                        color: Colors.purple,
                        fontWeight: FontWeight.bold,
                        fontSize: 20,
                      ),
                    ),
                    const Divider(color: Colors.white24),
                    Text(
                      "There is a ${confidence!.toStringAsFixed(2)}% chance that the "
                          "${displayedAsset?.toUpperCase()} market trend will be "
                          "${prediction == "0" ? "DOWNWARD" : prediction == "1" ? "UPWARD" : "STABLE"} tomorrow.",
                      textAlign: TextAlign.center,
                      style: TextStyle(
                        color: prediction == "1" ? Colors.purple : Colors.purple,
                        fontSize: 20,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    const SizedBox(height: 20),
                    if (graphData.isNotEmpty) buildAttractiveGraph(),
                  ],
                ),
              ),
            ),
          ),
        ),
        SizedBox(height: 10,),
        if(isnewsbuttonShow)
        Container(
          decoration: BoxDecoration(
            gradient: LinearGradient(
              colors: [Color(0xFF9C27B0), Color(0xFF673AB7)],
              begin: Alignment.topLeft,
              end: Alignment.bottomRight,
            ),
            boxShadow: [
              BoxShadow(
                color: Color(0xFF673AB7).withValues(alpha: 0.5),
                blurRadius: 15,
                offset: Offset(0, 5),
              ),
            ],
            borderRadius: BorderRadius.circular(30),
          ),
          child: ElevatedButton(
            onPressed: () {
              Navigator.push(
                context,
                MaterialPageRoute(builder: (context) => news_Screen(asset: displayedAsset!)),
              );
            },
            style: ElevatedButton.styleFrom(
              backgroundColor: Colors.transparent,
              shadowColor: Colors.transparent,
              foregroundColor: Colors.white,
              padding: EdgeInsets.symmetric(horizontal: 100, vertical: 15),
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(30),
              ),
            ),
            child: Text(
              "View $displayedAsset News",
              style: TextStyle(fontWeight: FontWeight.bold, fontSize: 15),
            ),
          ),
        )
      ],
    );
  }
}
