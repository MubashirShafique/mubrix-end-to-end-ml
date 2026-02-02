import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'package:url_launcher/url_launcher.dart';

class news_Screen extends StatefulWidget {
  final String asset;
  const news_Screen({super.key, required this.asset});

  @override
  State<news_Screen> createState() => _news_ScreenState();
}

class _news_ScreenState extends State<news_Screen> {
  final String apiKey = "pub_eb0cbabfbfc74655bb8fcbd7a99c6e0c";
  List newsList = [];
  bool isLoading = true;

  @override
  void initState() {
    super.initState();
    fetchNews();
  }

  Future<void> fetchNews() async {
    try {
      final response = await http.get(
        Uri.parse("https://newsdata.io/api/1/crypto?apikey=$apiKey&q=${widget.asset}"),
      );

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        setState(() {
          newsList = data['results'];
          isLoading = false;
        });
      }
    } catch (e) {
      setState(() => isLoading = false);
    }
  }

  Future<void> _launchURL(String urlString) async {
    final Uri url = Uri.parse(urlString);
    if (!await launchUrl(url, mode: LaunchMode.externalApplication)) {
      throw Exception('Could not launch $url');
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.black,
      appBar: AppBar(
        backgroundColor: Colors.black,
        iconTheme: const IconThemeData(color: Colors.white),
        title: Text(
          widget.asset.toUpperCase(),
          style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold),
        ),
        centerTitle: true,
      ),
      body: isLoading
          ? const Center(child: CircularProgressIndicator(color: Colors.purple))
          : ListView.builder(
        itemCount: newsList.length,
        itemBuilder: (context, index) {
          final article = newsList[index];
          return Card(
            color: Colors.grey[900],
            margin: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
            shape: RoundedRectangleBorder(
              side: const BorderSide(color: Colors.purple, width: 2),
              borderRadius: BorderRadius.circular(12),
            ),
            child: ListTile(
              contentPadding: const EdgeInsets.all(10),
              leading: ClipRRect(
                borderRadius: BorderRadius.circular(8),
                child: article['image_url'] != null
                    ? Image.network(
                  article['image_url'],
                  width: 80,
                  height: 80,
                  fit: BoxFit.cover,
                  errorBuilder: (context, error, stackTrace) =>
                  const Icon(Icons.broken_image, color: Colors.purple),
                )
                    : const Icon(Icons.newspaper, color: Colors.purple, size: 50),
              ),
              title: Text(
                article['title'] ?? 'No Title',
                style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold),
                maxLines: 2,
                overflow: TextOverflow.ellipsis,
              ),
              subtitle: Text(
                article['description'] ?? 'No Description available.',
                style: const TextStyle(color: Colors.white70),
                maxLines: 2,
                overflow: TextOverflow.ellipsis,
              ),
              onTap: () {
                if (article['link'] != null) {
                  _launchURL(article['link']);
                }
              },
            ),
          );
        },
      ),
    );
  }
}